from image_utils import Coordinate


class WvwMap:
    """
    Represents a WvW map. Should use the constants defined below.
    """

    def __init__(
            self,
            readable_name: str,
            gw2_api_name: str,
            discord_name: str,
            map_boundaries: tuple[Coordinate, Coordinate],
            image_path: str
    ):
        self.readable_name = readable_name
        self.gw2_api_name = gw2_api_name
        self.discord_name = discord_name
        self.map_boundaries = map_boundaries
        self.image_path = image_path

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

    def relative_gw2_api_coordinate(self, coordinates: Coordinate):
        """
        Relativize a given coordinate (using GW2 API units) onto this map. Coordinate
        will be returned where the map top left boundary acts as (0,0).
        """
        return coordinates.x - self.map_boundaries[0].x, coordinates.y - self.map_boundaries[0].y


# All known WvW maps
# image paths are relative to the command directories
# map boundaries are taken from the GW2 API

eternal_battlegrounds = WvwMap(
    readable_name='Eternal Battlegrounds',
    gw2_api_name='Center',
    discord_name='ebg',
    map_boundaries=(Coordinate(8958, 12798), Coordinate(12030, 15870)),
    image_path='img/ebg.png'
)

blue_borderlands = WvwMap(
    readable_name='Blue Borderlands (alpine)',
    gw2_api_name='BlueHome',
    discord_name='blue_bl',
    map_boundaries=(Coordinate(12798, 10878), Coordinate(15358, 14462)),
    image_path='img/blue_border.png'
)

green_borderlands = WvwMap(
    readable_name='Green Borderlands (alpine)',
    gw2_api_name='GreenHome',
    discord_name='green_bl',
    map_boundaries=(Coordinate(5630, 11518), Coordinate(8190, 15102)),
    image_path='img/green_border.jpg'
)

red_borderlands = WvwMap(
    readable_name='Red Borderlands (desert)',
    gw2_api_name='RedHome',
    discord_name='red_bl',
    map_boundaries=(Coordinate(9214, 8958), Coordinate(12286, 12030)),
    image_path='img/red_border.jpg'
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
        self.type = objective.get('type', 'Spawn')
        self.owner = objective.get('owner', 'Neutral')
        self.points_per_tick = objective['points_tick', 0]
        self.yak_count = objective['yaks_delivered', 0]

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
        self.red_percentage = round(self.red_ppt / self.total_ppt, 2) * 100
        self.green_percentage = round(self.green_ppt / self.total_ppt, 2) * 100
        self.blue_percentage = round(self.blue_ppt / self.total_ppt, 2) * 100
        self.neutral_percentage = round(self.neutral_ppt / self.total_ppt, 2) * 100

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
