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
from bot.commons import monitoring
from bot.commons import world_utils
from bot.commons import ssm_properties_utils
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
        if not ssm_properties_utils.is_world_functionality_enabled():
            template_utils.format_and_respond_world_functionality_disabled(discord_interactions, discord_utils, info)
            return

        loading_message = template_utils.get_localized_template(templates.updating_home_world, info.locale) \
            .format(emote_loading=discord_utils.animated_emote('loading', discord_utils.loading_emote_id))
        discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

        subcommand = discord_utils.extract_subcommand(event)
        if subcommand['name'] == 'set':
            home_world_name = discord_utils.extract_subcommand_option(subcommand, 'world_name')
            monitoring.log_command(info, 'home_world', 'add', home_world_name)
            # user provided new world, they want to set it: this must be authorized
            authorizer.authorize_command(guild_id, event)
            set_home_world(guild_id, home_world_name, info)
            print(f'Home world of guild with ID {str(guild_id)} was changed to {home_world_name}')
        elif subcommand['name'] == 'forget':
            monitoring.log_command(info, 'home_world', 'forget')
            authorizer.authorize_command(guild_id, event)
            delete_home_world(guild_id, info)
        else:  # view home world
            monitoring.log_command(info, 'home_world', 'view')
            get_home_world(guild_id, info)
    except common_exceptions.CommandUnauthorizedException:
        template_utils.format_and_respond_to_command_unauthorized(discord_interactions, discord_utils, info)
    except BaseException as e:
        print(f'Failed to do home world operation for guild with ID {guild_id}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def set_home_world(guild_id: str, home_world_name: str, info: discord_utils.InteractionInfo):
    try:
        home_world = world_utils.fetch_and_validate_gw2_world(home_world_name)
        # GW2 API says this world is valid, we can save it
        repo.save_guild_home_world(guild_id, home_world['id'], home_world['name'], home_world['population'])
        success_message = template_utils.get_localized_template(templates.home_world_set, info.locale)\
            .format(home_world=home_world_name)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except common_exceptions.InvalidWorldException as e:
        template_utils.format_and_respond_invalid_world(discord_interactions, info, e.world_name)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)


def delete_home_world(guild_id: str, info: discord_utils.InteractionInfo):
    repo.delete_home_world(guild_id)
    message = template_utils.get_localized_template(templates.home_word_forget, info.locale).format(
        emote_warning=discord_utils.default_emote('warning')
    )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, message)


def get_home_world(guild_id: str, info: discord_utils.InteractionInfo):
    try:
        # current selected home world
        home_world = repo.get_guild_home_world(guild_id)
        population = home_world['population']
        success_message = template_utils.get_localized_template(templates.home_world_get, info.locale)\
            .format(
                home_world=home_world['name'],
                home_world_population=get_localized_population(population, info.locale),
                transfer_cost=get_transfer_cost(population),
                emote_gem=discord_utils.custom_emote('gw2_gem', discord_utils.gem_emote_id)
            )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)
    except common_exceptions.HomeWorldNotSetException:
        template_utils.format_and_respond_home_world_not_set(discord_interactions, info)


def get_localized_population(population: str, locale: str) -> str:
    localized_populations = template_utils.get_localized_template(template_utils.populations, locale)
    return localized_populations[population]


def get_transfer_cost(population: str) -> str:
    return template_utils.transfer_costs[population]
