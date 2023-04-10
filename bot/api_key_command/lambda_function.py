import os
import traceback

import boto3

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import template_utils
from bot.commons import gw2_users
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
            gw2_user_repo.save_api_key(info.user_id, key)

            message = template_utils.get_localized_template(templates.key_added, info.locale)
            discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
            print(f'Saved new API key for user {info.username}, Discord ID {str(info.user_id)}. Key: {key}')
        else:  # must be delete
            gw2_user_repo.delete_api_key(info.user_id)
            message = template_utils.get_localized_template(templates.key_deleted, info.locale).format(
                emote_warning=discord_utils.default_emote('warning')
            )
            discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    except BaseException as e:
        print(f'Failed to save/delete API key of user with ID {str(info.user_id)}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)



