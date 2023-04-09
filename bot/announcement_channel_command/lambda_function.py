import os
import boto3

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
    if action == 'announcement_channel_add':
        add_announcement_channel(event, guild_id, info)
    elif action == 'announcement_channel_delete':
        remove_announcement_channel(event, guild_id, info)
    else:  # list, can be done by anyone
        list_announcement_channels(guild_id, info)


def add_announcement_channel(event, guild_id, info):
    try:
        authorizer.authorize_command(guild_id, event)
        channel_id = discord_utils.extract_option(event, 'channel_name')  # it's ID actually
        repo.add_announcement_channel(guild_id, channel_id)

        success_message = template_utils.get_localized_template(templates.channel_added, info.locale).format(
            channel=discord_utils.mention_channel(channel_id),
            emote_speaker=discord_utils.default_emote('loudspeaker')
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except common_exceptions.CommandUnauthorizedException:
        template_utils.format_and_respond_to_command_unauthorized(discord_interactions, discord_utils, info)
    except discord_utils.OptionNotFoundException:
        message = template_utils.get_localized_template(templates.channel_not_provided, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    except BaseException as e:
        print(f'Failed to add announcement channel for guild with ID {guild_id}')
        print(e)
        template_utils.format_and_respond_internal_error(discord_interactions, info)


def remove_announcement_channel(event, guild_id, info):
    try:
        authorizer.authorize_command(guild_id, event)
        channel_id = discord_utils.extract_option(event, 'channel_name')  # it's ID actually
        repo.delete_announcement_channel(guild_id, channel_id)

        success_message = template_utils.get_localized_template(templates.channel_deleted, info.locale).format(
            channel=discord_utils.mention_channel(channel_id),
            emote_mute=discord_utils.default_emote('mute')
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except common_exceptions.CommandUnauthorizedException:
        template_utils.format_and_respond_to_command_unauthorized(discord_interactions, discord_utils, info)
    except discord_utils.OptionNotFoundException:
        message = template_utils.get_localized_template(templates.channel_not_provided, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    except BaseException as e:
        print(f'Failed to remove announcement channel for guild with ID {guild_id}')
        print(e)
        template_utils.format_and_respond_internal_error(discord_interactions, info)


def list_announcement_channels(guild_id, info):
    try:
        channel_ids = repo.get_announcement_channels(guild_id)
        if len(channel_ids) > 0:
            message = template_utils.get_localized_template(templates.channels_listed, info.locale).format(
                channels=format_channel_names(channel_ids),
                emote_speaker=discord_utils.default_emote('loudspeaker')
            )
        else:
            message = template_utils.get_localized_template(templates.no_channels, info.locale).format(
                emote_mute=discord_utils.default_emote('mute')
            )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    except BaseException as e:
        print(f'Failed to list announcement channels for guild with ID {guild_id}')
        print(e)
        template_utils.format_and_respond_internal_error(discord_interactions, info)


def format_channel_names(channel_ids) -> str:
    channel_names = [discord_utils.mention_channel(channel_id) for channel_id in channel_ids]
    return ', '.join(channel_names)