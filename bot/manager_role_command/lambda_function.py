import os
import boto3
import botocore.client

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import gw2_guilds
from bot.commons import template_utils
from bot.commons import common_exceptions
from bot.commons import authorization
from . import templates

gw2_guilds_table_name = os.environ['GW2_GUILDS_TABLE_NAME']
dynamodb_resource = boto3.resource('dynamodb')
repo = gw2_guilds.Gw2GuildRepo(table_name=gw2_guilds_table_name, dynamodb_resource=dynamodb_resource)

authorizer = authorization.CommandAuthorizer(repo)


def lambda_handler(event, context):
    info = discord_utils.InteractionInfo(event)
    guild_id = discord_utils.extract_guild_id(event)

    action = discord_utils.extract_option(event, 'action')
    if action == 'manager_role_add':
        add_manager_role(event, guild_id, info)
    elif action == 'manager_role_delete':
        remove_manager_role(event, guild_id, info)
    else:  # list, can be done by anyone
        list_manager_roles(guild_id, info)


def add_manager_role(event, guild_id, info):
    try:
        authorizer.authorize_command(guild_id, event)

        role_id = discord_utils.extract_option(event, 'role')
        # TODO added variable not used for now
        added = repo.add_manager_role(guild_id, role_id)
        success_message = template_utils.get_localized_template(templates.manager_role_added, info.locale)\
            .format(role=discord_utils.mention_role(role_id))
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except common_exceptions.UserUnauthorizedException:
        error_message = template_utils.get_localized_template(
            template_map=template_utils.common_template_unauthorized,
            locale=info.locale
        ).format(emote_commander=discord_utils.custom_emote('commander', discord_utils.commander_emote_id))
        discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)
    except discord_utils.OptionNotFoundException:
        message = template_utils.get_localized_template(templates.role_not_provided, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    except botocore.client.ClientError as e:
        print(f'Failed to add manager role for guild with ID {guild_id}')
        print(e)
        error_message = template_utils.get_localized_template(template_utils.common_template_internal_error,
                                                              info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)


def remove_manager_role(event, guild_id, info):
    try:
        authorizer.authorize_command(guild_id, event)

        role_id = discord_utils.extract_option(event, 'role')
        # TODO removed variable not used for now
        removed = repo.delete_manager_role(guild_id, role_id)
        success_message = template_utils.get_localized_template(templates.manager_role_removed, info.locale) \
            .format(role=discord_utils.mention_role(role_id))
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except common_exceptions.UserUnauthorizedException:
        error_message = template_utils.get_localized_template(
            template_map=template_utils.common_template_unauthorized,
            locale=info.locale
        ).format(emote_commander=discord_utils.custom_emote('commander', discord_utils.commander_emote_id))
        discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)
    except discord_utils.OptionNotFoundException:
        message = template_utils.get_localized_template(templates.role_not_provided, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    except botocore.client.ClientError as e:
        print(f'Failed to remove manager role for guild with ID {guild_id}')
        print(e)
        error_message = template_utils.get_localized_template(template_utils.common_template_internal_error,
                                                              info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)


def list_manager_roles(guild_id, info):
    try:
        manager_roles = repo.get_manager_roles(guild_id)
        if len(manager_roles) > 0:
            roles_data = build_formatted_roles(manager_roles)
            success_message = template_utils.get_localized_template(templates.manager_role_listed, info.locale).format(roles=roles_data)
        else:
            success_message = template_utils.get_localized_template(templates.manager_roles_empty, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except botocore.client.ClientError as e:
        print(f'Failed to list manager roles for guild with ID {guild_id}')
        print(e)
        error_message = template_utils.get_localized_template(template_utils.common_template_internal_error,
                                                              info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)


def build_formatted_roles(role_ids) -> str:
    roles_data = ''
    for role_id in role_ids:
        roles_data += (discord_utils.mention_role(role_id) + ', ')
    return roles_data[:-2]
