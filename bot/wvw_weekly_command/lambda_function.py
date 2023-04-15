import traceback

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import template_utils
from bot.commons import monitoring
from . import templates


def lambda_handler(event, context):
    info = discord_utils.InteractionInfo(event)
    monitoring.log_command(info, 'wvw_weekly')
    try:
        message = compile_weekly_achievements(info)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    except BaseException as e:
        print(f'Error while responding to wvw weekly command of user {info.username}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def compile_weekly_achievements(info: discord_utils.InteractionInfo) -> str:
    potion_emote = discord_utils.custom_emote('wvw_potion', discord_utils.reward_potion_emote_id)
    detail_strings = []
    for weekly in templates.weekly_achievements:
        detail_string = template_utils.get_localized_template(templates.weekly_detail, info.locale).format(
            name=weekly['name'],
            amount=weekly['amount'],
            unit=template_utils.get_localized_template(weekly['unit'], info.locale),
            potion_amount=weekly['potion_reward'],
            emote_potion=potion_emote
        )
        detail_strings.append(detail_string)

    total_rewards_string = template_utils.get_localized_template(templates.total_rewards, info.locale).format(
        emote_gold=discord_utils.custom_emote('gw2_gold', discord_utils.gold_emote_id),
        emote_potion=potion_emote
    )

    summary_string = template_utils.get_localized_template(templates.summary, info.locale)

    return template_utils.get_localized_template(templates.achievements_response, info.locale).format(
        emote_wvw=discord_utils.custom_emote('wvw_icon', discord_utils.wvw_icon_id),
        achievement_details='\n'.join(detail_strings),
        total_rewards=total_rewards_string,
        summary=summary_string
    )
