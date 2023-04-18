import os
import traceback

import boto3
import pendulum
import pendulum.parsing

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import common_exceptions
from bot.commons import template_utils
from bot.commons import gw2_guilds
from bot.commons import authorization
from bot.commons import time_utils
from bot.commons import monitoring
from . import templates
from . import raid_scheduling

dynamodb_resource = boto3.resource('dynamodb')
gw2_guilds_table_name = os.environ['GW2_GUILDS_TABLE_NAME']
repo = gw2_guilds.Gw2GuildRepo(gw2_guilds_table_name, dynamodb_resource)

authorizer = authorization.CommandAuthorizer(repo)

max_raids = 10


def lambda_handler(event, context):
    """
    Handler for the 'wvw_raid' commands: this has 3 subcommands
    """
    info = discord_utils.extract_info(event)
    guild_id = info.guild_id
    subcommand = discord_utils.extract_subcommand(event)

    try:
        if subcommand['name'] == 'add':
            monitoring.log_command(info, 'wvw_raid', 'add')
            authorizer.authorize_command(guild_id, event)
            add_wvw_raid(subcommand, guild_id, info)
        elif subcommand['name'] == 'delete':
            monitoring.log_command(info, 'wvw_raid', 'delete')
            authorizer.authorize_command(guild_id, event)
            delete_wvw_raid(subcommand, guild_id, info)
        else:  # must be list, it can be done by anyone
            monitoring.log_command(info, 'wvw_raid', 'list')
            list_wvw_raids(guild_id, info)
    except common_exceptions.CommandUnauthorizedException:
        template_utils.format_and_respond_to_command_unauthorized(discord_interactions, discord_utils, info)
    except BaseException as e:
        print('Error while doing wvw raid operation')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def add_wvw_raid(subcommand, guild_id, info):
    try:
        if is_at_max(guild_id):
            error_message = template_utils.get_localized_template(templates.too_much, info.locale).format(max=str(max_raids))
            discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)
            return

        event_name: str = discord_utils.extract_subcommand_option(subcommand, 'name')
        day: str = discord_utils.extract_subcommand_option(subcommand, 'day')
        start_time: str = time_utils.validate_time_input(discord_utils.extract_subcommand_option(subcommand, 'start_time'))
        duration_hours: int = discord_utils.extract_subcommand_option(subcommand, 'duration')
        reminder_needed: bool = discord_utils.extract_subcommand_option(subcommand, 'reminder')

        if name_taken(guild_id, event_name):
            error_message = template_utils.get_localized_template(templates.name_taken, info.locale).format(name=event_name)
            discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)
            return

        wvw_raid = gw2_guilds.WvwRaid(event_name, day, start_time, duration_hours, reminder_needed)

        # schedule reminder of this raid if needed
        if reminder_needed:
            schedule_hash = raid_scheduling.create_schedule(guild_id, wvw_raid, info.locale)
            wvw_raid.set_schedule_hash(schedule_hash)

        repo.add_wvw_raid(guild_id, wvw_raid)

        message = template_utils.get_localized_template(templates.raid_added, info.locale).format(
            raid_description=create_raid_description(wvw_raid, info.locale)
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
    except pendulum.parsing.ParserError:
        message = template_utils.get_localized_template(templates.time_parsing_failed, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)


def is_at_max(guild_id: str) -> bool:
    return len(repo.list_wvw_raids(guild_id)) >= max_raids


def name_taken(guild_id: str, event_name: str) -> bool:
    raids = repo.list_wvw_raids(guild_id)
    for raid in raids:
        if raid.name == event_name:
            return True
    return False


def delete_wvw_raid(subcommand, guild_id, info):
    event_name: str = discord_utils.extract_subcommand_option(subcommand, 'name')
    delete_raid_schedule_if_needed(guild_id, event_name)
    deleted = repo.delete_wvw_raid(guild_id, event_name)
    if deleted:
        message = template_utils.get_localized_template(templates.raid_deleted, info.locale).format(event_name=event_name)
    else:
        message = template_utils.get_localized_template(templates.raid_not_found, info.locale).format(event_name=event_name)
    discord_interactions.respond_to_discord_interaction(info.interaction_token, message)


def delete_raid_schedule_if_needed(guild_id: str, event_name: str):
    for raid in repo.list_wvw_raids(guild_id):
        if raid.name == event_name and hasattr(raid, 'hash'):
            raid_scheduling.delete_schedule(raid.hash)


def list_wvw_raids(guild_id, info):
    raids = repo.list_wvw_raids(guild_id)
    if len(raids) > 0:
        message = template_utils.get_localized_template(templates.raids_listed, info.locale).format(
            raid_descriptions=create_all_raid_descriptions(raids, info.locale)
        )
    else:
        message = template_utils.get_localized_template(templates.raids_not_found, info.locale)
    discord_interactions.respond_to_discord_interaction(info.interaction_token, message)


def create_all_raid_descriptions(raids, locale: str) -> str:
    raids_sorted_by_days = sorted(raids, key=lambda x: time_utils.day_mappings[x.day])
    descriptions = []
    for raid in raids_sorted_by_days:
        descriptions.append(create_raid_description(raid, locale))
    return '\n'.join(descriptions)


def create_raid_description(raid: gw2_guilds.WvwRaid, locale: str) -> str:
    next_occurrence = time_utils.find_next_occurrence(raid.day, raid.time)
    description = template_utils.get_localized_template(templates.raid_description, locale).format(
        event_name=raid.name,
        day=template_utils.get_localized_template(time_utils.day_localizations, locale)[raid.day],
        time=raid.time,
        hours=raid.dur,
        next_occurrence=time_utils.format_date_time(next_occurrence),
        reminder_state=template_utils.get_localized_template(templates.reminder_states, locale)[raid.reminder]
    )
    return description
