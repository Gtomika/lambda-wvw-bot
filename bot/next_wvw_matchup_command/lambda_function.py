import os
import boto3
import traceback

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import common_exceptions
from bot.commons import template_utils
from bot.commons import gw2_api_interactions
from bot.commons import gw2_guilds
from bot.commons import matchup_utils
from . import templates

dynamodb_resource = boto3.resource('dynamodb')
gw2_guilds_table_name = os.environ['GW2_GUILDS_TABLE_NAME']
repo = gw2_guilds.Gw2GuildRepo(gw2_guilds_table_name, dynamodb_resource)


class RelinkException(Exception):
    pass


def lambda_handler(event, context):
    info = discord_utils.extract_info(event)
    guild_id = discord_utils.extract_guild_id(event)
    try:
        home_world = repo.get_guild_home_world(guild_id)

        loading_message = template_utils.get_localized_template(templates.matchup_calculation_in_progress, info.locale).format(
            emote_loading=discord_utils.animated_emote('loading', discord_utils.loading_emote_id)
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

        home_world = matchup_utils.WvwWorld(world_id=home_world['id'], world_name=home_world['name'])

        matchup = create_matchup_report(home_world.world_id)
        if matchup_utils.is_relink(matchup.end_at):
            raise RelinkException

        predicted_result, predicted_tier = predict_results(home_world.world_id, matchup)
        predicted_sides = predict_next_matchup_sides(
            current_matchup=matchup,
            predicted_tier=predicted_tier,
            predicted_result=predicted_result,
            home_world_side=matchup.get_side_of_world(home_world.world_id),
            home_world_placement=matchup.get_placement_of_world(home_world.world_id)
        )
        format_and_respond_with_prediction(info, predicted_sides, predicted_tier, predicted_result, home_world)
    except common_exceptions.NotFoundException:
        template_utils.format_and_response_home_world_not_set(discord_interactions, info)
    except RelinkException:
        error_message = template_utils.get_localized_template(templates.relink_response, info.locale)\
            .format(emote_link=discord_utils.default_emote('link'))
        discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)
    except gw2_api_interactions.ApiKeyUnauthorizedException:
        template_utils.format_and_respond_api_key_unauthorized(discord_interactions, discord_utils, info)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)
    except BaseException as e:
        print(f'Error while creating matchup report of guild with id {guild_id}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def format_and_respond_with_prediction(
        info: discord_utils.InteractionInfo,
        predicted_sides,
        predicted_tier: int,
        predicted_result: matchup_utils.MatchupResult,
        home_world: matchup_utils.WvwWorld
):
    prediction_string = template_utils.get_localized_template(templates.prediction, info.locale)[predicted_result.offset]\
        .format(
            tier=str(predicted_tier),
            emote=discord_utils.default_emote(predicted_result.emote_name)
        )

    side_strings = []
    for predicted_side in predicted_sides:
        is_home_side = predicted_side.contains_world(home_world.world_id)

        linked_world_names = [linked_world.world_name for linked_world in predicted_side.linked_worlds]
        linked_world_names_joined = ', '.join(linked_world_names)

        side_string = template_utils.get_localized_template(templates.predicted_team, info.locale).format(
            emote_color=discord_utils.default_emote(predicted_side.color.emote_name),
            emote_house=discord_utils.default_emote('house') if is_home_side else '',
            main_world_name=predicted_side.main_world.world_name,
            linked_world_names=linked_world_names_joined
        )
        side_strings.append(side_string)
    predicted_sides_string = '\n'.join(side_strings)

    success_message = template_utils.get_localized_template(templates.next_matchup_response, info.locale).format(
        home_world_name=home_world.world_name,
        emote_warning=discord_utils.default_emote('warning'),
        tier=str(predicted_tier - predicted_result.offset),
        prediction_string=prediction_string,
        predicted_teams_string=predicted_sides_string,
    )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)


def create_matchup_report(home_world_id: int) -> matchup_utils.Matchup:
    """
    Query and compile the current wvw matchup of the selected world.
    """
    matchup_data = gw2_api_interactions.get_wvw_matchup_report_of_world(world_id=home_world_id)
    return matchup_utils.parse_matchup(matchup_data, gw2_api_interactions)


def create_matchup_report_from_id(matchup_id: str) -> matchup_utils.Matchup:
    """
    Query and compile the selected matchup
    """
    matchup_data = gw2_api_interactions.get_wvw_matchup_report_by_id(matchup_id)
    return matchup_utils.parse_matchup(matchup_data, gw2_api_interactions)


def predict_results(home_world_id: int, matchup: matchup_utils.Matchup):
    """
    Makes a prediction on the results of the home world, based on the standing
    of the current matchup standings.
    """
    placement = matchup.get_placement_of_world(home_world_id)
    if placement == 1 and matchup.tier > 1:
        return matchup_utils.result_advances, matchup.tier - 1

    if placement == 3 and matchup.tier < matchup_utils.eu_lowest_tier:
        return matchup_utils.result_drops, matchup.tier + 1

    return matchup_utils.result_stays, matchup.tier


def predict_next_matchup_sides(
        current_matchup: matchup_utils.Matchup,
        predicted_tier: int,
        predicted_result: matchup_utils.MatchupResult,
        home_world_side: matchup_utils.MatchupSide,
        home_world_placement: int
):
    """
    Finds the sides that will participate in the home worlds next predicted WvW matchup.
     - current_matchup: State of current matchup of home: can be useful in some cases to reduce number of GW2 API calls
     - predicted_tier: Tier that home world is predicted to be in next matchup
     - predicted_result: Result of the home world's current matchup (for example "home world advances")
     - home_world_side: Side of the home world in the current matchup: this side will be part of next matchup too (though color may change)
     - home_world_placement: Placement of home world in current matchup: determines predicted color
    """
    predicted_sides = [home_world_side]  # home world side guaranteed to be present: but color is to be decided
    if predicted_result == matchup_utils.result_advances:
        predict_next_matchup_sides_if_home_advances(predicted_sides, predicted_tier, home_world_side)
    elif predicted_result == matchup_utils.result_drops:
        predict_next_matchup_sides_if_home_drops(predicted_sides, predicted_tier, home_world_side)
    else:  # stays in current tier
        predict_next_matchup_sides_if_home_stays(predicted_sides, current_matchup, predicted_tier, home_world_side, home_world_placement)
    return predicted_sides


def predict_next_matchup_sides_if_home_advances(
        predicted_sides,
        predicted_tier: int,
        home_world_side: matchup_utils.MatchupSide
):
    """
    Home world advances next tier. Find other 2 sides that are predicted to be in this next tier. These are to be
    added to 'predicted_sides'
    """
    if predicted_tier == 1:
        # predicted tier is top tier, no one will drop down here (home world advances + 2 side stays)
        predicted_tier_report = create_matchup_report_from_id(matchup_utils.build_matchup_id(matchup_utils.eu_region_constant, predicted_tier))
        first = predicted_tier_report.get_first_place()
        first.color = matchup_utils.green
        second = predicted_tier_report.get_second_place()
        second.color = matchup_utils.blue
        predicted_sides.extend([first, second])
    else:
        # predicted tier is not top, besides the home world, one side drops down here, and one will stay
        predicted_tier_report = create_matchup_report_from_id(matchup_utils.build_matchup_id(matchup_utils.eu_region_constant, predicted_tier))
        stays = predicted_tier_report.get_second_place()
        stays.color = matchup_utils.blue
        above_predicted_tier_report = create_matchup_report_from_id(matchup_utils.build_matchup_id(matchup_utils.eu_region_constant, predicted_tier - 1))
        drops_down = above_predicted_tier_report.get_third_place()
        drops_down.color = matchup_utils.green
        predicted_sides.extend([stays, drops_down])
    # because we advance (win), red color is guaranteed
    home_world_side.color = matchup_utils.red


def predict_next_matchup_sides_if_home_drops(
        predicted_sides,
        predicted_tier: int,
        home_world_side: matchup_utils.MatchupSide
):
    """
    Home world drops down a tier. Find other 2 sides that are predicted to be in this next tier. These are to be
    added to 'predicted_sides'
    """
    if predicted_tier == matchup_utils.eu_lowest_tier:
        # predicted tier is lowest, nobody advances here, instead 1 drops down (home) and 2 stays
        predicted_tier_report = create_matchup_report_from_id(matchup_utils.build_matchup_id(matchup_utils.eu_region_constant, predicted_tier))
        second = predicted_tier_report.get_second_place()
        second.color = matchup_utils.blue
        third = predicted_tier_report.get_third_place()
        third.color = matchup_utils.red
        predicted_sides.extend([second, third])
    else:
        # 1 stays in predicted tier and 1 advances from tier below
        predicted_tier_report = create_matchup_report_from_id(matchup_utils.build_matchup_id(matchup_utils.eu_region_constant, predicted_tier))
        stays = predicted_tier_report.get_second_place()
        stays.color = matchup_utils.blue
        below_predicted_tier_report = create_matchup_report_from_id(matchup_utils.build_matchup_id(matchup_utils.eu_region_constant, predicted_tier + 1))
        advances = below_predicted_tier_report.get_first_place()
        advances.color = matchup_utils.red
        predicted_sides.extend([stays, advances])
    # because we lose, green color is guaranteed
    home_world_side.color = matchup_utils.green


def predict_next_matchup_sides_if_home_stays(
        predicted_sides,
        current_matchup_report: matchup_utils.Matchup,
        predicted_tier: int,
        home_world_side: matchup_utils.MatchupSide,
        home_world_placement: int
):
    """
    Home world stays in the current tier. Find other 2 sides that are predicted to be in this next tier. These are to be
    added to 'predicted_sides'.
    Due to home world staying in current tier, this method can make use of already calculated current matchup
    """
    if predicted_tier == 1:  # home world stays in top tier (1)
        below_predicted_tier_report = create_matchup_report_from_id(matchup_utils.build_matchup_id(matchup_utils.eu_region_constant, predicted_tier + 1))
        advances = below_predicted_tier_report.get_first_place()
        advances.color = matchup_utils.red
        # home stays in tier 1, but is it first or second place? this determines the color
        if home_world_placement == 2:
            stays = current_matchup_report.get_first_place()
            stays.color = matchup_utils.green
            home_world_side.color = matchup_utils.blue
        else:  # home is first
            stays = current_matchup_report.get_second_place()
            stays.color = matchup_utils.blue
            home_world_side.color = matchup_utils.green
        predicted_sides.extend([advances, stays])
    elif predicted_sides == matchup_utils.eu_lowest_tier:  # home world stays in the lowest tier :(
        above_predicted_tier_report = create_matchup_report_from_id(matchup_utils.build_matchup_id(matchup_utils.eu_region_constant, predicted_tier - 1))
        drops = above_predicted_tier_report.get_third_place()
        drops.color = matchup_utils.green
        # home stays in tier 5, but is it seconds or third?
        if home_world_placement == 2:
            stays = current_matchup_report.get_third_place()
            stays.color = matchup_utils.red
            home_world_side.color = matchup_utils.blue
        else:  # home is third
            stays = current_matchup_report.get_second_place()
            stays.color = matchup_utils.blue
            home_world_side.color = matchup_utils.red
        predicted_sides.extend([drops, stays])
    else:  # home world is in some middle tier
        below_predicted_tier_report = create_matchup_report_from_id(matchup_utils.build_matchup_id(matchup_utils.eu_region_constant, predicted_tier + 1))
        advances = below_predicted_tier_report.get_first_place()
        advances.color = matchup_utils.red
        above_predicted_tier_report = create_matchup_report_from_id(matchup_utils.build_matchup_id(matchup_utils.eu_region_constant, predicted_tier - 1))
        drops = above_predicted_tier_report.get_third_place()
        drops.color = matchup_utils.green
        home_world_side.color = matchup_utils.blue
        predicted_sides.extend([advances, drops])

