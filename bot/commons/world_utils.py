from bot.commons import common_exceptions
from bot.commons import gw2_api_interactions
from bot.commons import discord_utils
from bot.commons import gw2_guilds


def fetch_and_validate_gw2_world(home_world_name: str):
    """
    Checks if this world name is valid, and returns the ID and population of it.
    Throws InvalidWorldException if this home world is invalid
    Throws ApiException if GW2 API failed
    """
    home_world_name = home_world_name.lower().strip()

    home_worlds_array = gw2_api_interactions.get_home_worlds()
    home_world = __find_home_world_with_name(home_worlds_array, home_world_name)
    return home_world['id'], home_world['population']


def __find_home_world_with_name(home_world_array, home_world: str):
    for home_world_item in home_world_array:
        if home_world_item['name'].lower() == home_world:
            return home_world_item
    raise common_exceptions.InvalidWorldException(home_world)


def identify_selected_world(guild_id: str, guilds_repo: gw2_guilds.Gw2GuildRepo, event) -> dict:
    """
    Find the world in which the caller is interested in. If the 'home_world' option is not specified,
    the command will fall back to the home world of the guild (HomeWorldNotSetException is thrown if not set).

    If the 'home_world' param is provided, it will be used to find appropriate world. NotFoundException is
    thrown if the selected value is invalid.
    """
    try:
        world_name = discord_utils.extract_option(event, 'world_name')
        # may throw not found exception
        world_id, population = fetch_and_validate_gw2_world(world_name)
        return {
            'id': world_id,
            'name': world_name,
            'population': population
        }
    except common_exceptions.OptionNotFoundException:
        # no name specified, fall back to guild home world, may throw HomeWorldNotSetException
        return guilds_repo.get_guild_home_world(guild_id)
