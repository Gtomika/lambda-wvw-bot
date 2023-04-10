import os
import traceback

import boto3

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import gw2_guilds
from bot.commons import gw2_api_interactions
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
    # guaranteed to be from a guild (by Discord)
    guild_id = discord_utils.extract_guild_id(event)

    try:
        loading_message = template_utils.get_localized_template(templates.updating_home_world, info.locale) \
            .format(emote_loading=discord_utils.animated_emote('loading', discord_utils.loading_emote_id))
        discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

        subcommand = discord_utils.extract_subcommand(event)
        if subcommand['name'] == 'set':
            home_world = discord_utils.extract_subcommand_option(subcommand, 'world_name')
            # user provided new world, they want to set it: this must be authorized
            authorizer.authorize_command(guild_id, event)
            set_home_world(guild_id, home_world, info)
            print(f'Home world of guild with ID {str(guild_id)} was changed to {home_world}')
        else:  # view home world
            get_home_world(guild_id, info)
    except common_exceptions.CommandUnauthorizedException:
        template_utils.format_and_respond_to_command_unauthorized(discord_interactions, discord_utils, info)
    except BaseException as e:
        print(f'Failed to do home world operation for guild with ID {guild_id}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def set_home_world(guild_id: str, home_world: str, info: discord_utils.InteractionInfo):
    try:
        home_world_id = validate_home_world(home_world)
        # GW2 API says this world is valid, we can save it
        repo.save_guild_home_world(guild_id, home_world_id)
        success_message = template_utils.get_localized_template(templates.home_world_set, info.locale)\
            .format(home_world=home_world)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except common_exceptions.NotFoundException:
        error_message = template_utils.get_localized_template(templates.invalid_home_world, info.locale).format(home_world=home_world)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)


def get_home_world(guild_id: str, info: discord_utils.InteractionInfo):
    try:
        # current selected home world
        home_world_id = repo.get_guild_home_world(guild_id)
        # get all worlds from API
        home_world_data = gw2_api_interactions.get_home_world_by_id(home_world_id)

        population = get_localized_population(home_world_data, info.locale)
        transfer_cost = get_transfer_cost(home_world_data)

        success_message = template_utils.get_localized_template(templates.home_world_get, info.locale)\
            .format(
                home_world=home_world_data['name'],
                home_world_population=population,
                transfer_cost=transfer_cost,
                emote_gem=discord_utils.custom_emote('gem', discord_utils.gem_emote_id)
            )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)
    except common_exceptions.NotFoundException:
        error_message = template_utils.get_localized_template(templates.home_world_not_set, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)


def validate_home_world(home_world: str) -> int:
    """
    Checks if this world name is valid, and returns the ID of it.
    Throws NotFoundException if this home world is invalid
    Throws ApiException if GW2 API failed
    """
    home_worlds_array = gw2_api_interactions.get_home_worlds()
    return find_home_world_with_name(home_worlds_array, home_world)['id']


def find_home_world_with_name(home_world_array, home_world: str):
    for home_world_item in home_world_array:
        if home_world_item['name'] == home_world:
            return home_world_item
    raise common_exceptions.NotFoundException


def get_localized_population(home_world_data, locale) -> str:
    population = home_world_data['population']
    localized_populations = template_utils.get_localized_template(templates.populations, locale)
    return localized_populations[population]


def get_transfer_cost(home_world_data) -> str:
    population = home_world_data['population']
    return templates.transfer_costs[population]
