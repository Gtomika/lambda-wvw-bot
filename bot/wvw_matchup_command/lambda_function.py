import os
import traceback

import boto3
import pendulum

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import common_exceptions
from bot.commons import template_utils
from bot.commons import gw2_api_interactions
from bot.commons import gw2_guilds
from bot.commons import matchup_utils
from bot.commons import time_utils
from bot.commons import monitoring
from . import templates

dynamodb_resource = boto3.resource('dynamodb')
gw2_guilds_table_name = os.environ['GW2_GUILDS_TABLE_NAME']
repo = gw2_guilds.Gw2GuildRepo(gw2_guilds_table_name, dynamodb_resource)


def lambda_handler(event, context):
    info = discord_utils.extract_info(event)
    monitoring.log_command(info, 'wvw_matchup')
    guild_id = info.guild_id
    try:
        home_world = repo.get_guild_home_world(guild_id)

        loading_message = template_utils.get_localized_template(templates.matchup_calculation_in_progress, info.locale).format(
            emote_loading=discord_utils.animated_emote('loading', discord_utils.loading_emote_id)
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

        home_world = matchup_utils.WvwWorld(world_id=home_world['id'], world_name=home_world['name'])

        matchup = create_matchup_report(home_world.world_id)
        success_message = format_matchup_report(home_world, matchup, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except common_exceptions.NotFoundException:
        template_utils.format_and_response_home_world_not_set(discord_interactions, info)
    except gw2_api_interactions.ApiKeyUnauthorizedException:
        template_utils.format_and_respond_api_key_unauthorized(discord_interactions, discord_utils, info)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)
    except BaseException as e:
        print(f'Error while creating matchup report of guild with id {guild_id}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def create_matchup_report(home_world_id: int) -> matchup_utils.Matchup:
    """
    Query and compile the current wvw matchup of the selected world.
    """
    matchup_data = gw2_api_interactions.get_wvw_matchup_report_of_world(world_id=home_world_id)
    return matchup_utils.parse_matchup(matchup_data, gw2_api_interactions)


def format_matchup_report(home_world: matchup_utils.WvwWorld, matchup: matchup_utils.Matchup, locale) -> str:
    # convert current and matchup end time to the desired locale
    time_zone = pendulum.timezone(template_utils.get_localized_template(matchup_utils.locale_time_zones, locale))
    current_time = pendulum.now(time_zone)
    reset_end_time = time_zone.convert(matchup.end_at)

    first_side = matchup.get_first_place()
    first_place_string = format_matchup_side(first_side, 1, first_side.contains_world(home_world.world_id), locale)

    second_side = matchup.get_second_place()
    second_place_string = format_matchup_side(second_side, 2, second_side.contains_world(home_world.world_id), locale)

    third_side = matchup.get_third_place()
    third_place_string = format_matchup_side(third_side, 3, third_side.contains_world(home_world.world_id), locale)

    return template_utils.get_localized_template(templates.matchup_report, locale).format(
        home_world_name=home_world.world_name,
        tier=matchup.tier,
        reset_time=time_utils.format_date_time(reset_end_time),
        emote_clock=discord_utils.default_emote('clock'),
        remaining_time=current_time.diff_for_humans(reset_end_time, absolute=True),
        matchup_side_first_place=first_place_string,
        matchup_side_second_place=second_place_string,
        matchup_side_third_place=third_place_string
    )


def format_matchup_side(side: matchup_utils.MatchupSide, placement: int, is_home_team: bool, locale) -> str:
    linked_world_names = [linked_world.world_name for linked_world in side.linked_worlds]
    linked_world_names_joined = ', '.join(linked_world_names)

    return template_utils.get_localized_template(templates.matchup_side_report, locale).format(
        emote_color=discord_utils.default_emote(side.color.emote_name),
        emote_house=discord_utils.default_emote('house') if is_home_team else '',
        main_world_name=side.main_world.world_name,
        linked_world_names=linked_world_names_joined,
        points=str(side.points),
        emote_placement=discord_utils.default_emote(matchup_utils.placement_emote_names[placement]),
        kills=str(side.kills),
        deaths=str(side.deaths),
        kd_ratio=str(side.kd_ratio)
    )
