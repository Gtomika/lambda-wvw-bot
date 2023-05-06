import pathlib
import json

from bot.commons import common_exceptions
from bot.commons import gw2_api_interactions
from bot.commons import discord_utils
from bot.commons import gw2_guilds


# this is static world data, not including population
commons_folder = pathlib.Path(__file__).parent.resolve()
with open(commons_folder.joinpath('data', 'wvw_worlds.json')) as worlds_file:
    __wvw_worlds_static = json.load(worlds_file)


def fetch_and_validate_gw2_world(home_world_name: str, static_data: bool = False):
    """
    Checks if this world name is valid, and returns the ID and population of it.
    If population is not required, use static world data to avoid GW2 API.
    Throws InvalidWorldException if this home world is invalid
    Throws ApiException if GW2 API failed
    """
    home_world_name = home_world_name.lower().strip()

    if static_data:
        home_worlds_array = __wvw_worlds_static
    else:
        home_worlds_array = gw2_api_interactions.get_home_worlds()

    return __find_home_world_with_name(home_worlds_array, home_world_name)


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
        return fetch_and_validate_gw2_world(world_name, static_data=True)
    except common_exceptions.OptionNotFoundException:
        # no name specified, fall back to guild home world, may throw HomeWorldNotSetException
        return guilds_repo.get_guild_home_world(guild_id)


def find_home_worlds_by_id(world_ids: list[int]) -> list[dict]:
    """
    Returns a list of home worlds with the given IDs. Static data is used, so the
    world population is not included.
    """
    return [world for world in __wvw_worlds_static if world['id'] in world_ids]
