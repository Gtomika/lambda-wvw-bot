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
    if action == 'wvw_role_add':
        add_wvw_role(event, guild_id, info)
    elif action == 'wvw_role_delete':
        remove_wvw_role(event, guild_id, info)
    else:  # list, can be done by anyone
        list_wvw_roles(guild_id, info)


def add_wvw_role(event, guild_id, info):
    try:
        authorizer.authorize_command(guild_id, event)

        role_id = discord_utils.extract_option(event, 'role')
        # TODO added variable not used for now
        added = repo.add_wvw_role(guild_id, role_id)
        success_message = template_utils.get_localized_template(templates.wvw_role_added, info.locale)\
            .format(role=discord_utils.mention_role(role_id))
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except common_exceptions.CommandUnauthorizedException:
        template_utils.format_and_respond_to_command_unauthorized(discord_interactions, discord_utils, info)
    except discord_utils.OptionNotFoundException:
        message = template_utils.get_localized_template(templates.role_not_provided, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    except botocore.client.ClientError as e:
        print(f'Failed to add wvw role for guild with ID {guild_id}')
        print(e)
        template_utils.format_and_respond_internal_error(discord_interactions, info)


def remove_wvw_role(event, guild_id, info):
    try:
        authorizer.authorize_command(guild_id, event)

        role_id = discord_utils.extract_option(event, 'role')
        # TODO removed variable not used for now
        removed = repo.delete_manager_role(guild_id, role_id)
        success_message = template_utils.get_localized_template(templates.wvw_role_removed, info.locale) \
            .format(role=discord_utils.mention_role(role_id))
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except common_exceptions.CommandUnauthorizedException:
        template_utils.format_and_respond_to_command_unauthorized(discord_interactions, discord_utils, info)
    except discord_utils.OptionNotFoundException:
        message = template_utils.get_localized_template(templates.role_not_provided, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    except botocore.client.ClientError as e:
        print(f'Failed to remove wvw role for guild with ID {guild_id}')
        print(e)
        template_utils.format_and_respond_internal_error(discord_interactions, info)


def list_wvw_roles(guild_id, info):
    try:
        manager_roles = repo.get_wvw_roles(guild_id)
        if len(manager_roles) > 0:
            roles_data = build_formatted_roles(manager_roles)
            success_message = template_utils.get_localized_template(templates.wvw_role_listed, info.locale).format(roles=roles_data)
        else:
            success_message = template_utils.get_localized_template(templates.wvw_roles_empty, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except botocore.client.ClientError as e:
        print(f'Failed to list wvw roles for guild with ID {guild_id}')
        print(e)
        template_utils.format_and_respond_internal_error(discord_interactions, info)


def build_formatted_roles(role_ids) -> str:
    roles_data = ''
    for role_id in role_ids:
        roles_data += (discord_utils.mention_role(role_id) + ', ')
    return roles_data[:-2]
