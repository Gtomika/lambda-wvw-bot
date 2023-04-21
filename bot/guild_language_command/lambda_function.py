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

emote_speak = discord_utils.default_emote('speaking_head')


def lambda_handler(event, context):
    info = discord_utils.InteractionInfo(event)
    try:
        subcommand = discord_utils.extract_subcommand(event)
        if subcommand['name'] == 'set':
            monitoring.log_command(info, 'guild_language', 'set')
            authorizer.authorize_command(info.guild_id, event)
            set_guild_language(subcommand, info)
        else:  # can only be 'view'
            monitoring.log_command(info, 'guild_language', 'view')
            view_guild_language(info)
    except common_exceptions.CommandUnauthorizedException:
        template_utils.format_and_respond_to_command_unauthorized(discord_interactions, discord_utils, info)
    except BaseException as e:
        print(f'Failed to set/view guild language for guild with ID {info.guild_id}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def set_guild_language(subcommand, info: discord_utils.InteractionInfo):
    # message selection is limited by slash command definition
    language = discord_utils.extract_subcommand_option(subcommand, 'language')
    repo.save_language(info.guild_id, language)

    message = template_utils.get_localized_template(templates.language_set, info.locale).format(
        language=language,
        emote_speak=emote_speak
    )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, message)


def view_guild_language(info: discord_utils.InteractionInfo):
    try:
        language = repo.get_language(info.guild_id)
        message = template_utils.get_localized_template(templates.language_view, info.locale).format(
            language=language,
            emote_speak=emote_speak
        )
    except common_exceptions.NotFoundException:
        message = template_utils.get_localized_template(templates.language_not_set, info.locale).format(
            emote_speak=emote_speak
        )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
