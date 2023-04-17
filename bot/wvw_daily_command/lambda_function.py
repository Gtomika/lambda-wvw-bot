import os
import traceback

import boto3

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import gw2_api_interactions
from bot.commons import gw2_users
from bot.commons import template_utils
from bot.commons import achievement_utils
from bot.commons import common_exceptions
from bot.commons import monitoring
from . import templates

dynamodb_resource = boto3.resource('dynamodb')
gw2_users_table_name = os.environ['GW2_USERS_TABLE_NAME']
repo = gw2_users.Gw2UsersRepo(gw2_users_table_name, dynamodb_resource)


def lambda_handler(event, context):
    info = discord_utils.InteractionInfo(event)
    monitoring.log_command(info, 'wvw_daily')
    try:
        loading_message = template_utils.get_localized_template(templates.loading, info.locale).format(
            emote_loading=discord_utils.animated_emote('loading', discord_utils.loading_emote_id)
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

        tomorrow = show_tomorrow(event)

        # it's an array of achievement IDs
        daily_wvw_achievements = gw2_api_interactions.get_daily_achievements(tomorrow)['wvw']
        daily_wvw_achievement_ids = [achi['id'] for achi in daily_wvw_achievements]

        # ask the details of these achievements from the API
        daily_wvw_achievements_details = gw2_api_interactions.get_achievements_by_ids(daily_wvw_achievement_ids)

        message = compile_daily_achievements(daily_wvw_achievements_details, tomorrow, info)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)
    except BaseException as e:
        print(f'Error while responding to wvw daily command of user {info.username}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def show_tomorrow(event) -> bool:
    try:
        return discord_utils.extract_option(event, 'tomorrow')
    except discord_utils.OptionNotFoundException:
        return False


# def fetch_progress_if_api_key_provided(user_id, daily_wvw_achievement_ids):
#     try:
#         api_key = repo.get_api_key(user_id)
#         return gw2_api_interactions.get_achievement_progress_by_ids(api_key, daily_wvw_achievement_ids)
#     except common_exceptions.NotFoundException:
#         return None  # user has no key, expected
#     except gw2_api_interactions.ApiKeyUnauthorizedException:
#         return None  # user has key without permissions, expected
#     except BaseException as e:
#         print(f'Exception while fetching daily wvw progress of user with ID {str(user_id)}')
#         traceback.print_exc()
#         return None


# progress_string = achievement_utils.create_achievement_progress_string(
#     locale=info.locale,
#     discord_utils=discord_utils,
#     template_utils=template_utils,
#     achievement=achievement,
#     progress_array=progress_array
# )
# detail_string = achievement_utils.create_daily_achievement_detail_string(
#     locale=info.locale,
#     template_utils=template_utils,
#     achievement=achievement,
#     reward_type=potion_emote,
#     progress=progress_string
# )

def compile_daily_achievements(achievement_details_array, tomorrow: bool, info: discord_utils.InteractionInfo) -> str:
    potion_emote = discord_utils.custom_emote('wvw_potion', discord_utils.reward_potion_emote_id)
    detail_strings = []
    for achievement in achievement_details_array:
        exotic_reward = achievement_utils.get_reward_amount_from_achievement(achievement, achievement_utils.wvw_exotic_reward_chest_id)
        detail_string = template_utils.get_localized_template(templates.daily_detail, info.locale).format(
            name=achievement['name'],
            description=achievement['requirement'],
            potion_amount=2 if exotic_reward >= 1 else 1,
            emote_potion=potion_emote
        )
        detail_strings.append(detail_string)

    total_rewards_string = template_utils.get_localized_template(templates.total_rewards, info.locale).format(
        emote_gold=discord_utils.custom_emote('gw2_gold', discord_utils.gold_emote_id)
    )

    summary_string = template_utils.get_localized_template(templates.summary_progress, info.locale)

    day_string = template_utils.get_localized_template(templates.today_tomorrow, info.locale)[tomorrow]

    return template_utils.get_localized_template(templates.achievements_response, info.locale).format(
        day=day_string,
        emote_wvw=discord_utils.custom_emote('wvw_icon', discord_utils.wvw_icon_id),
        achievement_details='\n'.join(detail_strings),
        total_rewards=total_rewards_string,
        summary=summary_string
    )



