import traceback
import boto3
import os

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import template_utils
from bot.commons import common_exceptions
from bot.commons import gw2_api_interactions
from bot.commons import gw2_users
from . import templates

dynamodb_resource = boto3.resource('dynamodb')
gw2_users_table_name = os.environ['GW2_USERS_TABLE_NAME']
repo = gw2_users.Gw2UsersRepo(gw2_users_table_name, dynamodb_resource)


def lambda_handler(event, context):
    info = discord_utils.InteractionInfo(event)
    try:
        loading_message = template_utils.get_localized_template(templates.loading, info.locale).format(
            emote_loading=discord_utils.animated_emote('loading', discord_utils.loading_emote_id)
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

        # it's an array of achievement IDs
        daily_wvw_achievements = gw2_api_interactions.get_daily_achievements()['wvw']
        daily_wvw_achievement_ids = [achi['id'] for achi in daily_wvw_achievements]

        # ask the details of these achievements from the API
        daily_wvw_achievements_details = gw2_api_interactions.get_achievements_by_ids(daily_wvw_achievement_ids)

        # ask how the user progressed with these achievements: may be None if no key was added
        progress_array = fetch_progress_if_api_key_provided(info.user_id, daily_wvw_achievement_ids)

        compile_daily_achievements(daily_wvw_achievements_details, progress_array, info)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)
    except BaseException as e:
        print(f'Error while responding to wvw daily command of user {info.username}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def fetch_progress_if_api_key_provided(user_id, daily_wvw_achievement_ids):
    try:
        api_key = repo.get_api_key(user_id)
        return gw2_api_interactions.get_achievement_progress_by_ids(api_key, daily_wvw_achievement_ids)
    except common_exceptions.NotFoundException:
        return None  # user has no key, expected
    except gw2_api_interactions.ApiKeyUnauthorizedException:
        return None  # user has key without permissions, expected
    except BaseException as e:
        print(f'Exception while fetching daily wvw progress of user with ID {str(user_id)}')
        traceback.print_exc()
        return None


def compile_daily_achievements(achievement_details_array, progress_array, info: discord_utils.InteractionInfo):
    detail_strings = []
    for achievement in achievement_details_array:
        detail_string = template_utils.get_localized_template(templates.achievement_detail, info.locale).format(
            name=achievement['name'],
            emote_status=achievement_status_emote(achievement['id'], progress_array),
            description=achievement['requirement'],
            potion_amount=str(gw2_api_interactions.get_reward_amount_from_achievement(achievement, gw2_api_interactions.wvw_potion_api_id)),
            emote_potion=discord_utils.custom_emote('wvw_potion', discord_utils.reward_potion_emote_id)

        )
        detail_strings.append(detail_string)

    total_rewards_string = template_utils.get_localized_template(templates.total_rewards, info.locale).format(
        emote_gold=discord_utils.custom_emote('gw2_gold', discord_utils.gold_emote_id)
    )

    if progress_array is not None:
        summary_string = template_utils.get_localized_template(templates.summary_progress, info.locale)
    else:
        summary_string = template_utils.get_localized_template(templates.summary_no_progress, info.locale)

    message = template_utils.get_localized_template(templates.achievements_response, info.locale).format(
        emote_notes=discord_utils.default_emote('notebook'),
        achievement_details='\n'.join(detail_strings),
        total_rewards=total_rewards_string,
        summary=summary_string
    )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, message)


def achievement_status_emote(achievement_id: int, progress_array):
    """
    Find status of achi from progress array and return appropriate emote. Progress array may be None!
    """
    if progress_array is None:
        return ''  # do not show any state
    for achi_progress in progress_array:
        if achi_progress['id'] == achievement_id:
            return discord_utils.default_emote('white_check_mark') if achi_progress['done'] else discord_utils.default_emote('x')
    return ''  # not expected
