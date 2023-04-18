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

app_name = os.environ['APP_NAME']
app_icon_url = os.environ['APP_ICON_URL']
webhook_personality = discord_interactions.WebhookPersonality(app_name, app_icon_url)

announcement_channel_max = 3


def lambda_handler(event, context):
    info = discord_utils.InteractionInfo(event)
    guild_id = discord_utils.extract_guild_id(event)

    try:
        subcommand = discord_utils.extract_subcommand(event)
        if subcommand['name'] == 'add':
            monitoring.log_command(info, 'announcement_channel', 'add')
            authorizer.authorize_command(guild_id, event)
            add_announcement_channel(subcommand, guild_id, info)
        elif subcommand['name'] == 'delete':
            monitoring.log_command(info, 'announcement_channel', 'delete')
            authorizer.authorize_command(guild_id, event)
            remove_announcement_channel(subcommand, guild_id, info)
        else:  # list, can be done by anyone
            monitoring.log_command(info, 'announcement_channel', 'list')
            list_announcement_channels(guild_id, info)
    except common_exceptions.CommandUnauthorizedException:
        template_utils.format_and_respond_to_command_unauthorized(discord_interactions, discord_utils, info)
    except BaseException as e:
        print(f'Failed to add/delete/list announcement channel for guild with ID {guild_id}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def add_announcement_channel(subcommand, guild_id, info):
    try:
        if is_at_max(guild_id):
            error_message = template_utils.get_localized_template(templates.too_much, info.locale).format(max=str(announcement_channel_max))
            discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)
            return

        channel_id = discord_utils.extract_subcommand_option(subcommand, 'channel')  # it's ID actually
        webhook_url = discord_utils.extract_subcommand_option(subcommand, 'webhook_url')
        repo.put_announcement_channel(guild_id, channel_id, webhook_url)

        test_webhook_message = template_utils.get_localized_template(templates.webhook_test, info.locale).format(
            emote_success=discord_utils.default_emote('white_check_mark')
        )
        discord_interactions.create_webhook_message(webhook_url, test_webhook_message, webhook_personality)

        success_message = template_utils.get_localized_template(templates.channel_added, info.locale).format(
            channel=discord_utils.mention_channel(channel_id),
            emote_speaker=discord_utils.default_emote('loudspeaker')
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except discord_utils.OptionNotFoundException:
        message = template_utils.get_localized_template(templates.channel_not_provided, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)


def is_at_max(guild_id) -> bool:
    return len(repo.get_announcement_channels(guild_id)) >= announcement_channel_max


def remove_announcement_channel(subcommand, guild_id, info):
    try:
        channel_id = discord_utils.extract_subcommand_option(subcommand, 'channel')  # it's ID actually
        previous_webhook = repo.delete_announcement_channel(guild_id, channel_id)

        if previous_webhook is not None:
            goodbye_message = template_utils.get_localized_template(templates.goodbye_message, info.locale).format(
                emote_wave=discord_utils.default_emote('wave')
            )
            discord_interactions.create_webhook_message(previous_webhook, goodbye_message, webhook_personality)

        success_message = template_utils.get_localized_template(templates.channel_deleted, info.locale).format(
            channel=discord_utils.mention_channel(channel_id),
            emote_mute=discord_utils.default_emote('mute')
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except discord_utils.OptionNotFoundException:
        message = template_utils.get_localized_template(templates.channel_not_provided, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)


def list_announcement_channels(guild_id, info):
    channel_ids = [channel_data['id'] for channel_data in repo.get_announcement_channels(guild_id)]
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


def format_channel_names(channel_ids) -> str:
    channel_names = [discord_utils.mention_channel(channel_id) for channel_id in channel_ids]
    return ', '.join(channel_names)
