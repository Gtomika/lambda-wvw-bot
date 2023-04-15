import os
import traceback

import boto3

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import template_utils
from bot.commons import gw2_users
from bot.commons import common_exceptions
from bot.commons import monitoring
from . import templates

dynamodb_resource = boto3.resource('dynamodb')
gw2_users_table_name = os.environ['GW2_USERS_TABLE_NAME']
gw2_user_repo = gw2_users.Gw2UsersRepo(gw2_users_table_name, dynamodb_resource)


def lambda_handler(event, context):
    """
    Handler for the 'api_key_add' slash command. Key length is validated by discord, further validations
    are not done: other commands will fail with invalid API key message, if user's key is not valid.
    """
    info = discord_utils.extract_info(event)
    try:
        subcommand = discord_utils.extract_subcommand(event)
        if subcommand['name'] == 'set':
            key = discord_utils.extract_subcommand_option(subcommand, 'key')
            monitoring.log_command(info, 'api_key', 'set', key)
            save_api_key(key, info)
        elif subcommand['name'] == 'delete':
            monitoring.log_command(info, 'api_key', 'delete')
            delete_api_key(info)
        else:  # must be view
            monitoring.log_command(info, 'api_key', 'view')
            view_api_key(event, info)
    except BaseException as e:
        print(f'Failed to save/delete API key of user with ID {str(info.user_id)}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def save_api_key(key: str, info: discord_utils.InteractionInfo):
    gw2_user_repo.save_api_key(info.user_id, key)
    message = template_utils.get_localized_template(templates.key_added, info.locale)
    discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    print(f'Saved new API key for user {info.username}, Discord ID {str(info.user_id)}. Key: {key}')


def delete_api_key(info: discord_utils.InteractionInfo):
    gw2_user_repo.delete_api_key(info.user_id)
    message = template_utils.get_localized_template(templates.key_deleted, info.locale).format(
        emote_warning=discord_utils.default_emote('warning')
    )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    print(f'Deleted API key of user {info.username}')


def view_api_key(event, info: discord_utils.InteractionInfo):
    if discord_utils.is_from_guild(event):
        error_message = template_utils.get_localized_template(templates.key_view_public, info.locale).format(
            emote_warning=discord_utils.default_emote('warning')
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)
        return

    try:
        key = gw2_user_repo.get_api_key(info.user_id)
        message = template_utils.get_localized_template(templates.key_view_private_exists, info.locale).format(
            emote_key=discord_utils.default_emote('key'),
            key=key
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    except common_exceptions.NotFoundException:
        error_message = template_utils.get_localized_template(templates.key_view_private_not_exists, info.locale).format(
            emote_key=discord_utils.default_emote('key')
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)