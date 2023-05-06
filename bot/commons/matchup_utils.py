import pendulum

from bot.commons import world_utils


eu_region_constant = 2
eu_lowest_tier = 5
reset_time_summer = 20
reset_time_winter = 19

placement_emote_names = {
    1: 'first_place',
    2: 'second_place',
    3: 'third_place'
}


class MatchupException(Exception):
    pass


class Color:
    """
    Possible sides of a Wvw Matchup. Use defined constants
    """

    def __init__(self, color_string, emote_name):
        self.color_string = color_string
        self.emote_name = emote_name


red = Color('red', 'red_circle')
blue = Color('blue', 'blue_circle')
green = Color('green', 'green_circle')


class WvwWorld:
    """
    Represents one world (server) that takes part in GW2 WvW. A side consist of
    multiple worlds, and a matchup is a battle between sides.
    """

    def __init__(self, world_id: int, world_name: str):
        self.world_id = world_id
        self.world_name = world_name

    def __eq__(self, other):
        return self.world_id == other.world_id and self.world_name == other.world_name


class MatchupSide:
    """
    Represents one of the 3 combatant teams in wvw. It can consist of
    multiple worlds (main one + paired ones)
    """

    def __init__(self, color: Color, main_world: WvwWorld, linked_worlds: list[WvwWorld], points: int, kills: int, deaths: int, kd_ratio: float):
        self.color = color
        self.main_world = main_world
        self.linked_worlds = linked_worlds
        self.points = points
        self.kills = kills
        self.deaths = deaths
        self.kd_ratio = kd_ratio

    def contains_world(self, world_id: int):
        if world_id == self.main_world.world_id:
            return True
        for linked_world in self.linked_worlds:
            if world_id == linked_world.world_id:
                return True
        return False


class Matchup:
    """
    Represents a Wvw matchup: 3 combatant teams with 'MatchupSide' classes
    """

    def __init__(self, tier: int, end_at: pendulum.DateTime, sides):
        self.tier = tier
        self.end_at = end_at
        self.sides = sorted(sides, key=lambda x: x.points, reverse=True)

    def get_first_place(self) -> MatchupSide:
        return self.sides[0]

    def get_second_place(self) -> MatchupSide:
        return self.sides[1]

    def get_third_place(self) -> MatchupSide:
        return self.sides[2]

    def get_placement_of_world(self, world_id: int) -> int:
        """
        Given a world ID, it finds what is the placement of this world in the matchup.
        """
        if self.get_first_place().contains_world(world_id):
            return 1
        elif self.get_second_place().contains_world(world_id):
            return 2
        else:
            return 3

    def get_side_of_world(self, world_id: int) -> MatchupSide:
        """
        Given a world ID it find the side of this world from the matchup
        Throws: MatchupException if this world is not in the matchup (not expected)
        """
        for side in self.sides:
            if side.contains_world(world_id):
                return side
        raise MatchupException

    def get_main_world_of_team(self, color: Color) -> WvwWorld:
        for side in self.sides:
            if side.color == color:
                return side.main_world
        raise MatchupException(f'Internal error: no side with color {str(color)}')

    def get_linked_worlds_of_team(self, color: Color) -> list[WvwWorld]:
        for side in self.sides:
            if side.color == color:
                return side.linked_worlds
        raise MatchupException(f'Internal error: no side with color {str(color)}')


class MatchupResult:
    """
    The result of a Wvw matchup for a single world. Use constant values of it.
    """

    def __init__(self, offset: int, emote_name: str):
        self.offset = offset
        self.emote_name = emote_name

    def __eq__(self, other):
        return self.offset == other.offset


result_advances = MatchupResult(1, 'arrow_up')
result_stays = MatchupResult(0, 'chains')
result_drops = MatchupResult(-1, 'arrow_down')


def build_matchup_id(region_id: int, tier: int) -> str:
    return f'{str(region_id)}-{str(tier)}'


def parse_matchup(matchup_api_data) -> Matchup:
    """
    Parse matchup data from Gw2 API response. Time zone should be
    selected from 'locale_time_zones' map based on request locale.
    """
    tier = __parse_tier(matchup_api_data['id'])
    end_time = pendulum.parse(matchup_api_data['end_time'])
    red_side = __parse_matchup_side(matchup_api_data, red)
    blue_side = __parse_matchup_side(matchup_api_data, blue)
    green_side = __parse_matchup_side(matchup_api_data, green)
    return Matchup(tier=tier, end_at=end_time, sides=[red_side, green_side, blue_side])  # sorting is done inside class


def __parse_matchup_side(matchup_api_data, color: Color) -> MatchupSide:
    # extract worlds IDs: main + linked
    main_world_id = matchup_api_data['worlds'][color.color_string]
    all_world_ids = matchup_api_data['all_worlds'][color.color_string]

    # make request to gw2 API to get names for these world IDs
    worlds_data = world_utils.find_home_worlds_by_id(all_world_ids)
    all_worlds = __parse_worlds_data(worlds_data)
    main_world = __pick_main_world(all_worlds, main_world_id)

    linked_worlds = all_worlds
    linked_worlds.remove(main_world)

    # extract additional data
    kills = matchup_api_data['kills'][color.color_string]
    deaths = matchup_api_data['deaths'][color.color_string]
    kd_ratio = round(float(kills) / float(deaths), 3)
    points = matchup_api_data['victory_points'][color.color_string]

    return MatchupSide(color=color, main_world=main_world, linked_worlds=linked_worlds,
                       points=points, kills=kills, deaths=deaths, kd_ratio=kd_ratio)


def __parse_worlds_data(worlds_data):
    worlds = []
    for world_data in worlds_data:
        worlds.append(WvwWorld(world_id=world_data['id'], world_name=world_data['name']))
    return worlds


def __pick_main_world(worlds, main_world_id):
    for world in worlds:
        if world.world_id == main_world_id:
            return world


def __parse_tier(matchup_id: str) -> int:
    parts = matchup_id.split('-')
    return int(parts[1])  # part 0 is region, part 1 is tier


def is_relink(next_reset_time: pendulum.DateTime) -> bool:
    """
    Relink is on odd months last friday.
    """
    now = pendulum.now()
    is_odd_month = now.month % 2 != 0
    if is_odd_month:
        # re-link is on the last friday of this month
        relink_day = now.last_of(unit="month", day_of_week=pendulum.FRIDAY)
        # we have already passed this re-link, even though it was this month
        if relink_day.is_past():
            relink_day = now.add(months=1).last_of(unit='month', day_of_week=pendulum.FRIDAY)
    else:
        # re-link is on the last friday of NEXT month
        relink_day = now.add(months=1).last_of(unit='month', day_of_week=pendulum.FRIDAY)
    return next_reset_time.is_same_day(relink_day)

