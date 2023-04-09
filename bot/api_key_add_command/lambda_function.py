import os
import boto3

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import template_utils
from bot.commons import gw2_api_interactions
from bot.commons import gw2_users
from . import templates

required_key_length = 72

dynamodb_resource = boto3.resource('dynamodb')
gw2_users_table_name = os.environ['GW2_USERS_TABLE_NAME']
gw2_user_repo = gw2_users.Gw2UsersRepo(gw2_users_table_name, dynamodb_resource)


def lambda_handler(event, context):
    """
    Handler for the 'api_key_add' slash command
    """

    interaction_info = discord_utils.extract_info(event)
    key = discord_utils.extract_option(event, option_name='key')
    is_valid, message = validate_api_key(key, interaction_info.locale)

    # key is valid, proceed to save
    if is_valid:
        try:
            gw2_user_repo.save_api_key(interaction_info.user_id, key)
            # message does not need to be changed
            print(f'Saved new API key for user {interaction_info.username}, Discord ID {str(interaction_info.user_id)}. Key: {key}')
            discord_interactions.respond_to_discord_interaction(interaction_info.interaction_token, message)
        except BaseException as e:
            print(f'Failed to save API key of user with ID {str(interaction_info.user_id)}')
            print(e)
            # some error prevented the valid key from saving
            template_utils.format_and_respond_internal_error(discord_interactions, interaction_info)
    else:
        print(f'Key that user {interaction_info.username} sent was invalid: {key}')
        discord_interactions.respond_to_discord_interaction(interaction_info.interaction_token, message)


def validate_api_key(key: str, locale: str):
    """
    Validates the given API key: first there is a length check, then a real
    call to the GW2 API is made with this key.

    Returns 2 values: bool success indicator and a response message
    """

    # format validations
    if len(key) != required_key_length:
        message = template_utils.get_localized_template(templates.invalid_key_response_template, locale).format(
            emote_key=discord_utils.default_emote('key'),
            api_key_length=required_key_length,
            api_key_url=discord_utils.escaped_link(template_utils.anet_accounts_url)
        )
        return False, message

    # format should be valid, check key with real call
    try:
        account = gw2_api_interactions.get_account(key)
    except gw2_api_interactions.ApiKeyUnauthorizedException:
        message = template_utils.get_localized_template(templates.unauthorized_response_template, locale).format(
            emote_no_entry=discord_utils.default_emote('no_entry_sign'),
            permissions=template_utils.gw2_api_permissions
        )
        return False, message
    except gw2_api_interactions.ApiException as e:
        print(f'Unexpected exception while validating API key against GW2 API: {str(e)}')
        message = template_utils.get_localized_template(templates.api_error_response_template, locale)\
            .format(emote_no_entry=discord_utils.default_emote('no_entry_sign'))
        return False, message

    # key valid, because GW2 API responded
    message = template_utils.get_localized_template(templates.success_response_template, locale).format(
        emote_key=discord_utils.default_emote('key'),
        gw2_account_name=account['name']
    )
    return True, message

