import traceback

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import template_utils
from bot.commons import gw2_api_interactions
from . import templates


def lambda_handler(event, context):
    info = discord_utils.InteractionInfo(event)
    try:
        # it's an array of achievement IDs
        daily_wvw_achievements = gw2_api_interactions.get_daily_achievements()['wvw']
        daily_wvw_achievement_ids = [achi['id'] for achi in daily_wvw_achievements]

        # ask the details of these achievements from the API
        daily_wvw_achievements_details = gw2_api_interactions.get_achievements_by_ids(daily_wvw_achievement_ids)
        compile_daily_achievements(daily_wvw_achievements_details, info)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)
    except BaseException as e:
        print(f'Error while responding to wvw daily command of user {info.username}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def compile_daily_achievements(details, info: discord_utils.InteractionInfo):
    detail_strings = []
    for achievement in details:
        detail_string = template_utils.get_localized_template(templates.achievement_detail, info.locale).format(
            name=achievement['name'],
            description=achievement['requirement']
        )
        detail_strings.append(detail_string)

    message = template_utils.get_localized_template(templates.achievements_response, info.locale).format(
        emote_notes=discord_utils.default_emote('notebook'),
        achievement_details='\n'.join(detail_strings),
        emote_three=discord_utils.default_emote('three')
    )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, message)