import json
from typing import Union
import pathlib

from bot.commons import image_utils


# objectives are loaded from file once
# this is static objective data, not including actual state (for example how owns the objectives)
# that depends on the matchup!!!
commons_folder = pathlib.Path(__file__).parent.resolve()
with open(commons_folder.joinpath('data', 'wvw_objectives.json')) as objectives_file:
    wvw_objectives_static = json.load(objectives_file)


class WvwMap:
    """
    Represents a WvW map. Should use the constants defined below.
    """

    def __init__(
            self,
            readable_name: str,
            gw2_api_name: str,
            discord_name: str,
            map_boundaries: tuple[image_utils.Coordinate, image_utils.Coordinate],
            image_path: str,
            color_code: int
    ):
        self.readable_name = readable_name
        self.gw2_api_name = gw2_api_name
        self.discord_name = discord_name
        self.map_boundaries = map_boundaries
        self.image_path = image_path
        self.color_code = color_code

    def width_gw2_api(self):
        """
        Width of this map in the units used by the GW2 API.
        """
        return self.map_boundaries[1].x - self.map_boundaries[0].x

    def height_gw2_api(self):
        """
        Height of this map in the units used by the GW2 API.
        """
        return self.map_boundaries[1].y - self.map_boundaries[0].y

    def relative_gw2_api_coordinate(self, coordinates: image_utils.Coordinate) -> image_utils.Coordinate:
        """
        Relativize a given coordinate (using GW2 API units) onto this map. Coordinate
        will be returned where the map top left boundary acts as (0,0).
        """
        return image_utils.Coordinate(coordinates.x - self.map_boundaries[0].x, coordinates.y - self.map_boundaries[0].y)


# All known WvW maps
# image paths are relative to the command directories
# map boundaries are taken from the GW2 API

eternal_battlegrounds = WvwMap(
    readable_name='Eternal Battlegrounds',
    gw2_api_name='Center',
    discord_name='ebg',
    map_boundaries=(image_utils.Coordinate(8958, 12798), image_utils.Coordinate(12030, 15870)),
    image_path='img/ebg.jpg',
    color_code=12745742
)

blue_borderlands = WvwMap(
    readable_name='Blue Borderlands (alpine)',
    gw2_api_name='BlueHome',
    discord_name='blue_bl',
    map_boundaries=(image_utils.Coordinate(12798, 10878), image_utils.Coordinate(15358, 14462)),
    image_path='img/blue_border.jpg',
    color_code=3447003
)

green_borderlands = WvwMap(
    readable_name='Green Borderlands (alpine)',
    gw2_api_name='GreenHome',
    discord_name='green_bl',
    map_boundaries=(image_utils.Coordinate(5630, 11518), image_utils.Coordinate(8190, 15102)),
    image_path='img/green_border.jpg',
    color_code=5763719
)

red_borderlands = WvwMap(
    readable_name='Red Borderlands (desert)',
    gw2_api_name='RedHome',
    discord_name='red_bl',
    map_boundaries=(image_utils.Coordinate(9214, 8958), image_utils.Coordinate(12286, 12030)),
    image_path='img/red_border.jpg',
    color_code=15548997
)


def select_map(map_discord_name: str) -> WvwMap:
    if map_discord_name == eternal_battlegrounds.discord_name:
        return eternal_battlegrounds
    elif map_discord_name == green_borderlands.discord_name:
        return green_borderlands
    elif map_discord_name == blue_borderlands.discord_name:
        return blue_borderlands
    elif map_discord_name == red_borderlands.discord_name:
        return red_borderlands
    else:
        raise Exception(f'Internal error, map discord name {map_discord_name} is invalid')


upgrade_1_yak_requirement = 20
upgrade_2_yak_requirement = 40
upgrade_3_yak_requirement = 80


class WvwObjective:
    """
    Represents a WwW objective, including current state
    """

    def __init__(self, objective: dict):
        """
        Construct an objective from a GW2 API description of it.
        """
        self.id = objective.get('id', 0)
        self.name = objective.get('name', 'Unknown')
        self.type = objective.get('type', 'Spawn')
        self.map_name_gw2_api = objective.get('map_type', 'Unknown')
        self.owner = objective.get('owner', 'Neutral')

        self.points_per_tick = objective.get('points_tick', 0)
        self.yak_count = objective.get('yaks_delivered', 0)

        # for reasons unimaginable, 'Mercenary' objects have no 'coord' in the API, but 'label_coord' instead
        raw_coordinate = objective.get('coord' if self.type != 'Mercenary' else 'label_coord', [0, 0])
        self.coordinate = image_utils.Coordinate(raw_coordinate[0], raw_coordinate[1])


    def get_upgrade_tier(self) -> int:
        """
        Calculate the upgrade tier based on the objective type and the yak count.
        0 is returned if the objective is not upgraded or cannot be upgraded (such as for 'Spawn')
        """
        if self.yak_count >= upgrade_3_yak_requirement:
            return 3
        elif self.yak_count >= upgrade_2_yak_requirement:
            return 2
        elif self.yak_count >= upgrade_3_yak_requirement:
            return 1
        else:  # for non-upgradable objectives it will be 0
            return 0

    def get_image_path(self) -> Union[str, None]:
        """
        Find the appropriate image path for this objective. It depends on the objective type
        and the owner of the objective. Some objectives will not have an image and None is returned.
        """
        if self.type == 'Camp' or self.type == 'Tower' or self.type == 'Keep' \
                or self.type == 'Castle' or self.type == 'Mercenary' or self.type == 'Ruins':
            return f'img/{self.type.lower()}_{self.owner.lower()}.png'
        else:
            return None

    def get_upgrade_image_path(self) -> Union[str, None]:
        """
        Find the appropriate upgrade image for this objective. The upgrade tier
        will be calculated based on the objective type and the yak count. If the objective is not upgraded
        or cannot be upgraded (such as for 'Spawn'), None is returned.
        """
        upgrade_tier = self.get_upgrade_tier()
        if upgrade_tier == 0:
            return None
        return f'img/upgrade_{upgrade_tier}.png'


class WvwMapDominance:
    """
    A class to store the distribution of points across teams on a WvW map.
    Such as 50% dominance of red team, 25%-25% of green and blue team.
    Dominance is based on the points that the teams objectives generate.
    """

    def __init__(self, objectives):
        """
        List of WvwObjective objects expected. They are expected to be in the same map.
        """
        self.total_ppt, self.red_ppt, self.green_ppt, self.blue_ppt, self.neutral_ppt = self.__calculate_dominance(objectives)
        self.red_percentage = round((self.red_ppt / self.total_ppt) * 100)
        self.green_percentage = round((self.green_ppt / self.total_ppt) * 100)
        self.blue_percentage = round((self.blue_ppt / self.total_ppt) * 100)
        self.neutral_percentage = round((self.neutral_ppt / self.total_ppt) * 100)

    def __calculate_dominance(self, objectives) -> tuple[int, int, int, int, int]:
        total_ppt = red_ppt = green_ppt = blue_ppt = neutral_ppt = 0
        for objective in objectives:
            if objective.owner == 'Red':
                red_ppt += objective.points_per_tick
            elif objective.owner == 'Green':
                green_ppt += objective.points_per_tick
            elif objective.owner == 'Blue':
                blue_ppt += objective.points_per_tick
            elif objective.owner == 'Neutral':
                neutral_ppt += objective.points_per_tick
            else:
                print(f'Unknown side {objective.owner} for an objective, points per tick of this objective wont be counted')
                continue
            total_ppt += objective.points_per_tick
        return total_ppt, red_ppt, green_ppt, blue_ppt, neutral_ppt


def get_wvw_objectives_from_map(wvw_map: WvwMap, matchup_raw: dict) -> list[WvwObjective]:
    """
    Return a list of WvwObjective objects from a WvW map. The matchup data is used to
    fill in the actual state of the objectives.
    """
    # find the desired map from the matchup data
    objectives_matchup_data = [matchup_map['objectives'] for matchup_map in matchup_raw['maps']
                               if matchup_map['type'] == wvw_map.gw2_api_name][0]

    # need to merge the static objectives data with the matchup data
    __merge_objectives(objectives_matchup_data, wvw_objectives_static)

    # parse into objects
    return [WvwObjective(objective) for objective in objectives_matchup_data]


def __merge_objectives(objectives_matchup_data: list[dict], objectives_static_data: list[dict]):
    """
    Create dictionaries for which contain all objective data (static and matchup data).
    Only those objectives will be present which are in 'objectives_matchup_data'.
    """
    for matchup_objective in objectives_matchup_data:
        # find appropriate objective in static data
        found = False

        for static_objective in objectives_static_data:
            if matchup_objective['id'] == static_objective['id']:
                matchup_objective.update(static_objective)
                found = True
                break

        if not found:
            print(f'Could not find objective {matchup_objective["id"]} in static data. This objective will not be included.')
