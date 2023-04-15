import os
import traceback

import boto3

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import gw2_guilds
from bot.commons import template_utils
from bot.commons import common_exceptions
from bot.commons import authorization
from bot.commons import monitoring
from . import templates

gw2_guilds_table_name = os.environ['GW2_GUILDS_TABLE_NAME']
dynamodb_resource = boto3.resource('dynamodb')
repo = gw2_guilds.Gw2GuildRepo(table_name=gw2_guilds_table_name, dynamodb_resource=dynamodb_resource)

authorizer = authorization.CommandAuthorizer(repo)

max_roles = 3


def lambda_handler(event, context):
    info = discord_utils.InteractionInfo(event)
    guild_id = info.guild_id

    try:
        subcommand = discord_utils.extract_subcommand(event)
        if subcommand['name'] == 'add':
            monitoring.log_command(info, 'wvw_role', 'add')
            authorizer.authorize_command(guild_id, event)
            add_wvw_role(subcommand, guild_id, info)
        elif subcommand['name'] == 'delete':
            monitoring.log_command(info, 'wvw_role', 'delete')
            authorizer.authorize_command(guild_id, event)
            remove_wvw_role(subcommand, guild_id, info)
        else:  # list, can be done by anyone
            monitoring.log_command(info, 'wvw_role', 'list')
            list_wvw_roles(guild_id, info)
    except common_exceptions.CommandUnauthorizedException:
        template_utils.format_and_respond_to_command_unauthorized(discord_interactions, discord_utils, info)
    except BaseException as e:
        print(f'Failed to add/delete/list wvw role for guild with ID {guild_id}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def add_wvw_role(subcommand, guild_id, info):
    try:
        role_id = discord_utils.extract_subcommand_option(subcommand, 'role')

        if is_at_max(guild_id):
            error_message = template_utils.get_localized_template(templates.too_much, info.locale).format(max=str(max_roles))
            discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)
            return

        repo.add_wvw_role(guild_id, role_id)
        success_message = template_utils.get_localized_template(templates.wvw_role_added, info.locale)\
            .format(role=discord_utils.mention_role(role_id))
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except discord_utils.OptionNotFoundException:
        message = template_utils.get_localized_template(templates.role_not_provided, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)


def is_at_max(guild_id: str) -> bool:
    return len(repo.get_wvw_roles(guild_id)) >= max_roles


def remove_wvw_role(subcommand, guild_id, info):
    try:
        role_id = discord_utils.extract_subcommand_option(subcommand, 'role')
        repo.delete_manager_role(guild_id, role_id)
        success_message = template_utils.get_localized_template(templates.wvw_role_removed, info.locale) \
            .format(role=discord_utils.mention_role(role_id))
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except discord_utils.OptionNotFoundException:
        message = template_utils.get_localized_template(templates.role_not_provided, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)


def list_wvw_roles(guild_id, info):
    manager_roles = repo.get_wvw_roles(guild_id)
    if len(manager_roles) > 0:
        roles_data = build_formatted_roles(manager_roles)
        success_message = template_utils.get_localized_template(templates.wvw_role_listed, info.locale).format(roles=roles_data)
    else:
        success_message = template_utils.get_localized_template(templates.wvw_roles_empty, info.locale)
    discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)


def build_formatted_roles(role_ids) -> str:
    roles_data = ''
    for role_id in role_ids:
        roles_data += (discord_utils.mention_role(role_id) + ', ')
    return roles_data[:-2]
