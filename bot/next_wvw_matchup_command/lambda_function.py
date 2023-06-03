import os
import boto3
import traceback

import pendulum

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import common_exceptions
from bot.commons import template_utils
from bot.commons import gw2_api_interactions
from bot.commons import gw2_guilds
from bot.commons import matchup_utils
from bot.commons import monitoring
from bot.commons import world_utils
from . import templates

dynamodb_resource = boto3.resource('dynamodb')
gw2_guilds_table_name = os.environ['GW2_GUILDS_TABLE_NAME']
repo = gw2_guilds.Gw2GuildRepo(gw2_guilds_table_name, dynamodb_resource)


def lambda_handler(event, context):
    info = discord_utils.extract_info(event)
    monitoring.log_command(info, 'next_wvw_matchup')
    guild_id = info.guild_id
    try:
        home_world = world_utils.identify_selected_world(guild_id, repo, event)

        loading_message = template_utils.get_localized_template(templates.matchup_calculation_in_progress, info.locale).format(
            emote_loading=discord_utils.animated_emote('loading', discord_utils.loading_emote_id)
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

        home_world = matchup_utils.WvwWorld(world_id=home_world['id'], world_name=home_world['name'])

        raw_matchup_data = gw2_api_interactions.get_wvw_matchup_report_of_world(home_world.world_id)
        matchup = matchup_utils.parse_matchup(raw_matchup_data)

        predicted_result, predicted_tier = matchup_utils.predict_results(home_world.world_id, matchup)
        predicted_sides = matchup_utils.predict_next_matchup_sides(
            current_matchup=matchup,
            predicted_tier=predicted_tier,
            predicted_result=predicted_result,
            home_world_side=matchup.get_side_of_world(home_world.world_id),
            home_world_placement=matchup.get_placement_of_world(home_world.world_id)
        )
        prediction_response = format_matchup_prediction(
            predicted_sides, predicted_tier, predicted_result, home_world, matchup.end_at, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, prediction_response)
    except common_exceptions.HomeWorldNotSetException:
        template_utils.format_and_respond_home_world_not_set(discord_interactions, info)
    except common_exceptions.InvalidWorldException as e:
        template_utils.format_and_response_invalid_world(discord_interactions, info, e.world_name)
    except gw2_api_interactions.ApiKeyUnauthorizedException:
        template_utils.format_and_respond_api_key_unauthorized(discord_interactions, discord_utils, info)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)
    except BaseException as e:
        print(f'Error while creating matchup report of guild with id {guild_id}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def format_matchup_prediction(
        predicted_sides: list[matchup_utils.MatchupSide],
        predicted_tier: int,
        predicted_result: matchup_utils.MatchupResult,
        home_world: matchup_utils.WvwWorld,
        matchup_end_date: pendulum.DateTime,
        locale: str
) -> str:
    if matchup_utils.is_relink(matchup_end_date):
        matchup_prediction_string = template_utils.get_localized_template(matchup_utils.relink_prediction, locale).format(
            emote_link=discord_utils.default_emote('link')
        )
    else:
        matchup_prediction_string = matchup_utils.build_matchup_prediction_string(
            predicted_sides=predicted_sides,
            predicted_tier=predicted_tier,
            predicted_result=predicted_result,
            home_world=home_world,
            locale=locale
        )
    return template_utils.get_localized_template(templates.next_matchup_response, locale).format(
        home_world_name=home_world.world_name,
        matchup_prediction=matchup_prediction_string,
        emote_warning=discord_utils.default_emote('warning'),
    )


