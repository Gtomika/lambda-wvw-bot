import traceback
import os
import boto3

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import template_utils
from bot.commons import monitoring
from bot.commons import gw2_users
from bot.commons import gw2_api_interactions
from bot.commons import common_exceptions
from bot.commons import wizards_vault_utils
from . import templates

dynamodb_resource = boto3.resource('dynamodb')
gw2_users_table_name = os.environ['GW2_USERS_TABLE_NAME']
gw2_user_repo = gw2_users.Gw2UsersRepo(gw2_users_table_name, dynamodb_resource)

astral_acclaim_emote = discord_utils.custom_emote('astral_acclaim', discord_utils.astral_acclaim_emote_id)
complete_emote = discord_utils.default_emote('white_check_mark')


def lambda_handler(event, context):
    info = discord_utils.InteractionInfo(event)
    monitoring.log_command(info, 'wvw_weekly')
    try:
        weekly_type = discord_utils.extract_option(event, 'weekly_type')
        if weekly_type == 'weekly_type_legacy':
            message = compile_weekly_legacy_achievements(info)
        else: # weekly type Wizard's Vault
            api_key = gw2_user_repo.get_api_key(info.user_id)
            weekly_wizards_vault_response = gw2_api_interactions.get_wizards_vault_weekly(api_key)
            message = wizards_vault_utils.create_wizards_vault_objectives_message(
                wizards_vault_utils.period_weekly,
                weekly_wizards_vault_response,
                info.locale
            )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    except common_exceptions.NotFoundException:
        template_utils.format_and_respond_api_key_required(discord_interactions, discord_utils, info)
    except gw2_api_interactions.ApiKeyUnauthorizedException:
        template_utils.format_and_respond_api_key_unauthorized(discord_interactions, discord_utils, info)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)
    except BaseException as e:
        print(f'Error while responding to wvw weekly command of user {info.username}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def compile_weekly_legacy_achievements(info: discord_utils.InteractionInfo) -> str:
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