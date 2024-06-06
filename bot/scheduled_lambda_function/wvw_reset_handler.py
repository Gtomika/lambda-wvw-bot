import traceback

import pendulum
import typing

from bot.commons import gw2_guilds
from bot.commons import matchup_utils
from bot.commons import discord_utils
from bot.commons import discord_interactions
from bot.commons import template_utils
from bot.commons import gw2_api_interactions
from bot.commons import ssm_properties_utils
from . import templates
from . import scheduled_lambda_utils

# will contain raw matchup data: speeds up the processing if multiple guilds
# have the same home world set
raw_matchup_data_cache = {}


def handle_wvw_reset_event(
    guilds_repo: gw2_guilds.Gw2GuildRepo,
    personality: discord_interactions.WebhookPersonality
):
    """
    An event where guilds must be notified about wvw reset. Includes relink too.
    """
    for guild in guilds_repo.find_all_guilds([
        gw2_guilds.home_world_field_name,
        gw2_guilds.announcement_channels_field_name,
        gw2_guilds.wvw_roles_field_name,
        gw2_guilds.language_field_name
    ]):
        locale = scheduled_lambda_utils.get_guild_language_or_default(guild)
        if gw2_guilds.home_world_field_name in guild:
            home_world = matchup_utils.WvwWorld(guild[gw2_guilds.home_world_field_name]['id'], guild[gw2_guilds.home_world_field_name]['name'])
            # check for relink. invoked on friday, so we can assume today is the reset day
            is_relink = matchup_utils.is_relink(pendulum.today())
            if is_relink:
                # world data not used here, as we cannot predict it for relink
                reminder_string = compile_reminder_string(None, locale, build_relink_prediction)
            else:
                # world data IS used here, so we must check if it is disabled
                if not ssm_properties_utils.is_world_functionality_enabled():
                    reminder_string = compile_reminder_string(home_world, locale, build_world_functionality_disabled_prediction)
                else:
                    reminder_string = compile_reminder_string(home_world, locale, build_standard_prediction)
        else:
            # world data not used here, as guild does not have home world set, and we don't know it
            reminder_string = compile_reminder_string(None, locale, build_no_home_world_set_prediction)

        wvw_role_ids = scheduled_lambda_utils.get_guild_attribute_or_empty(guild, gw2_guilds.wvw_roles_field_name)
        if len(wvw_role_ids) > 0:
            wvw_role_mentions = discord_utils.mention_multiple_roles(wvw_role_ids)
            personalized_reminder_string = f'{reminder_string}\n{wvw_role_mentions}'
        else:
            personalized_reminder_string = reminder_string

        announcement_channels = scheduled_lambda_utils.get_guild_attribute_or_empty(guild, gw2_guilds.announcement_channels_field_name)
        scheduled_lambda_utils.post_to_announcement_channels(
            guild_id=guild[gw2_guilds.guild_id_field_name],
            announcement_channels=announcement_channels,
            personality=personality,
            message=personalized_reminder_string
        )


def compile_reminder_string(
        home_world: typing.Union[matchup_utils.WvwWorld, None],
        locale: str,
        matchup_prediction_string_builder: typing.Callable[[typing.Union[matchup_utils.WvwWorld, None], str], str]
):
    commander_emote = discord_utils.custom_emote('commander', discord_utils.commander_emote_id)
    summary_string = template_utils.get_localized_template(templates.wvw_reset_summary, locale).format(
        emote_commander=commander_emote
    )

    matchup_prediction_string = matchup_prediction_string_builder(home_world, locale)

    return template_utils.get_localized_template(templates.wvw_reset_reminder, locale).format(
        emote_wvw=discord_utils.custom_emote('wvw_icon', discord_utils.wvw_icon_id),
        matchup_prediction_string=matchup_prediction_string,
        summary_string=summary_string
    )


def build_no_home_world_set_prediction(home_world: None, locale: str) -> str:
    """
    Home world parameter added to match expected function arguments, but it's unused.
    """
    return template_utils.get_localized_template(templates.home_world_not_set, locale)


def build_relink_prediction(home_world: None, locale: str) -> str:
    """
    Home world parameter added to match expected function arguments, but it's unused.
    """
    return template_utils.get_localized_template(matchup_utils.relink_prediction, locale).format(
        emote_link=discord_utils.default_emote('link')
    )


def build_world_functionality_disabled_prediction(home_world: matchup_utils.WvwWorld, locale: str) -> str:
    """
    Home world parameter added to match expected function arguments, but it's unused.
    """
    return template_utils.get_localized_template(template_utils.common_template_world_functionality_disabled, locale).format(
        emote_scream=discord_utils.default_emote('scream'),
        developer=discord_utils.mention_user(discord_utils.developer_id),
        emote_tools=discord_utils.default_emote('tools')
    )


def build_standard_prediction(home_world: matchup_utils.WvwWorld, locale: str) -> str:
    try:
        raw_matchup_data = cached_get_matchup_data(home_world.world_id)
        matchup = matchup_utils.parse_matchup(raw_matchup_data)

        predicted_result, predicted_tier = matchup_utils.predict_results(home_world.world_id, matchup)
        predicted_sides = matchup_utils.predict_next_matchup_sides(
            current_matchup=matchup,
            predicted_tier=predicted_tier,
            predicted_result=predicted_result,
            home_world_side=matchup.get_side_of_world(home_world.world_id),
            home_world_placement=matchup.get_placement_of_world(home_world.world_id)
        )

        return matchup_utils.build_matchup_prediction_string(
            predicted_sides=predicted_sides,
            predicted_tier=predicted_tier,
            predicted_result=predicted_result,
            home_world=home_world,
            locale=locale
        )
    except gw2_api_interactions.ApiException as e:
        print(f'The GW2 API failed to return the matchup data for world with ID {home_world.world_id}.'
              f' Reset prediction cannot be compiled: {str(e)}')
        traceback.print_exc()
        return template_utils.get_localized_template(templates.api_error, locale).format(
            emote_cry=discord_utils.default_emote('cry')
        )


def cached_get_matchup_data(world_id: int) -> dict:
    """
    Search the cache for the matchup data. If not found, it is fetched from the API and cached.
    This improves performance when multiple guilds have the same home world set.

    This method can raise an exception if the API fails the return the matchup data!
    """
    if world_id in raw_matchup_data_cache:
        return raw_matchup_data_cache[world_id]
    else:
        raw_matchup_data = gw2_api_interactions.get_wvw_matchup_report_of_world(world_id)
        raw_matchup_data_cache[world_id] = raw_matchup_data
        return raw_matchup_data
