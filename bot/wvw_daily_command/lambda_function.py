import os
import traceback

import boto3

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import gw2_api_interactions
from bot.commons import gw2_users
from bot.commons import template_utils
from bot.commons import wizards_vault_utils
from bot.commons import common_exceptions
from bot.commons import monitoring

dynamodb_resource = boto3.resource('dynamodb')
gw2_users_table_name = os.environ['GW2_USERS_TABLE_NAME']
repo = gw2_users.Gw2UsersRepo(gw2_users_table_name, dynamodb_resource)

astral_acclaim_emote = discord_utils.custom_emote('astral_acclaim', discord_utils.astral_acclaim_emote_id)
complete_emote = discord_utils.default_emote('white_check_mark')


def lambda_handler(event, context):
    info = discord_utils.InteractionInfo(event)
    monitoring.log_command(info, 'wvw_daily')
    try:
        api_key = repo.get_api_key(info.user_id)
        gw2_api_wizards_vault_response = gw2_api_interactions.get_wizards_vault_daily(api_key)
        message = wizards_vault_utils.create_wizards_vault_objectives_message(
            wizards_vault_utils.period_daily,
            gw2_api_wizards_vault_response,
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
        print(f'Error while responding to wvw daily command of user {info.username}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)
