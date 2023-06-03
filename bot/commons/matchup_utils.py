import pendulum

from bot.commons import world_utils
from bot.commons import discord_utils
from bot.commons import template_utils
from bot.commons import gw2_api_interactions

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


def predict_results(home_world_id: int, matchup: Matchup):
    """
    Makes a prediction on the results of the home world, based on the standing
    of the current matchup standings.
    """
    placement = matchup.get_placement_of_world(home_world_id)
    if placement == 1 and matchup.tier > 1:
        return result_advances, matchup.tier - 1

    if placement == 3 and matchup.tier < eu_lowest_tier:
        return result_drops, matchup.tier + 1

    return result_stays, matchup.tier


def predict_next_matchup_sides(
        current_matchup: Matchup,
        predicted_tier: int,
        predicted_result: MatchupResult,
        home_world_side: MatchupSide,
        home_world_placement: int
):
    """
    Finds the sides that will participate in the home worlds next predicted WvW matchup.
     - current_matchup: State of current matchup of home: can be useful in some cases to reduce number of GW2 API calls
     - predicted_tier: Tier that home world is predicted to be in next matchup
     - predicted_result: Result of the home world's current matchup (for example "home world advances")
     - home_world_side: Side of the home world in the current matchup: this side will be part of next matchup too (though color may change)
     - home_world_placement: Placement of home world in current matchup: determines predicted color
    """
    predicted_sides = [home_world_side]  # home world side guaranteed to be present: but color is to be decided
    if predicted_result == result_advances:
        predict_next_matchup_sides_if_home_advances(predicted_sides, predicted_tier, home_world_side)
    elif predicted_result == result_drops:
        predict_next_matchup_sides_if_home_drops(predicted_sides, predicted_tier, home_world_side)
    else:  # stays in current tier
        predict_next_matchup_sides_if_home_stays(predicted_sides, current_matchup, predicted_tier, home_world_side, home_world_placement)
    return predicted_sides


def predict_next_matchup_sides_if_home_advances(
        predicted_sides,
        predicted_tier: int,
        home_world_side: MatchupSide
):
    """
    Home world advances next tier. Find other 2 sides that are predicted to be in this next tier. These are to be
    added to 'predicted_sides'
    """
    if predicted_tier == 1:
        # predicted tier is top tier, no one will drop down here (home world advances + 2 side stays)
        predicted_tier_report = create_matchup_report_from_id(build_matchup_id(eu_region_constant, predicted_tier))
        first = predicted_tier_report.get_first_place()
        first.color = green
        second = predicted_tier_report.get_second_place()
        second.color = blue
        predicted_sides.extend([first, second])
    else:
        # predicted tier is not top, besides the home world, one side drops down here, and one will stay
        predicted_tier_report = create_matchup_report_from_id(build_matchup_id(eu_region_constant, predicted_tier))
        stays = predicted_tier_report.get_second_place()
        stays.color = blue
        above_predicted_tier_report = create_matchup_report_from_id(build_matchup_id(eu_region_constant, predicted_tier - 1))
        drops_down = above_predicted_tier_report.get_third_place()
        drops_down.color = green
        predicted_sides.extend([stays, drops_down])
    # because we advance (win), red color is guaranteed
    home_world_side.color = red


def predict_next_matchup_sides_if_home_drops(
        predicted_sides,
        predicted_tier: int,
        home_world_side: MatchupSide
):
    """
    Home world drops down a tier. Find other 2 sides that are predicted to be in this next tier. These are to be
    added to 'predicted_sides'
    """
    if predicted_tier == eu_lowest_tier:
        # predicted tier is lowest, nobody advances here, instead 1 drops down (home) and 2 stays
        predicted_tier_report = create_matchup_report_from_id(build_matchup_id(eu_region_constant, predicted_tier))
        second = predicted_tier_report.get_second_place()
        second.color = blue
        third = predicted_tier_report.get_third_place()
        third.color = red
        predicted_sides.extend([second, third])
    else:
        # 1 stays in predicted tier and 1 advances from tier below
        predicted_tier_report = create_matchup_report_from_id(build_matchup_id(eu_region_constant, predicted_tier))
        stays = predicted_tier_report.get_second_place()
        stays.color = blue
        below_predicted_tier_report = create_matchup_report_from_id(build_matchup_id(eu_region_constant, predicted_tier + 1))
        advances = below_predicted_tier_report.get_first_place()
        advances.color = red
        predicted_sides.extend([stays, advances])
    # because we lose, green color is guaranteed
    home_world_side.color = green


def predict_next_matchup_sides_if_home_stays(
        predicted_sides,
        current_matchup_report: Matchup,
        predicted_tier: int,
        home_world_side: MatchupSide,
        home_world_placement: int
):
    """
    Home world stays in the current tier. Find other 2 sides that are predicted to be in this next tier. These are to be
    added to 'predicted_sides'.
    Due to home world staying in current tier, this method can make use of already calculated current matchup
    """
    if predicted_tier == 1:  # home world stays in top tier (1)
        below_predicted_tier_report = create_matchup_report_from_id(build_matchup_id(eu_region_constant, predicted_tier + 1))
        advances = below_predicted_tier_report.get_first_place()
        advances.color = red
        # home stays in tier 1, but is it first or second place? this determines the color
        if home_world_placement == 2:
            stays = current_matchup_report.get_first_place()
            stays.color = green
            home_world_side.color = blue
        else:  # home is first
            stays = current_matchup_report.get_second_place()
            stays.color = blue
            home_world_side.color = green
        predicted_sides.extend([advances, stays])
    elif predicted_sides == eu_lowest_tier:  # home world stays in the lowest tier :(
        above_predicted_tier_report = create_matchup_report_from_id(build_matchup_id(eu_region_constant, predicted_tier - 1))
        drops = above_predicted_tier_report.get_third_place()
        drops.color = green
        # home stays in tier 5, but is it seconds or third?
        if home_world_placement == 2:
            stays = current_matchup_report.get_third_place()
            stays.color = red
            home_world_side.color = blue
        else:  # home is third
            stays = current_matchup_report.get_second_place()
            stays.color = blue
            home_world_side.color = red
        predicted_sides.extend([drops, stays])
    else:  # home world is in some middle tier
        below_predicted_tier_report = create_matchup_report_from_id(build_matchup_id(eu_region_constant, predicted_tier + 1))
        advances = below_predicted_tier_report.get_first_place()
        advances.color = red
        above_predicted_tier_report = create_matchup_report_from_id(build_matchup_id(eu_region_constant, predicted_tier - 1))
        drops = above_predicted_tier_report.get_third_place()
        drops.color = green
        home_world_side.color = blue
        predicted_sides.extend([advances, drops])


def create_matchup_report_from_id(matchup_id: str) -> Matchup:
    raw_report = gw2_api_interactions.get_wvw_matchup_report_by_id(matchup_id)
    return parse_matchup(raw_report)


# used by multiple commands, and so placed here instead of a templates.py file.
relink_prediction = {
    'hu': 'Re-link lesz {emote_link}, a párosított világok megváltoznak. Most semmit sem lehet tudni a következő matchupról.',
    'en': 'It will be re-link {emote_link} and the paired worlds change. Nothing is known about the next matchup.'
}

matchup_prediction = {
    'en': '''Current world tier: Tier {tier}
{tier_prediction_string}

These worlds may be in the next matchup:
{predicted_sides_string}''',
    'hu': '''A világ jelenlegi szintje: Tier {tier}
{tier_prediction_string}

Ezek a szerverek lehetnek a következő matchup-ban:
{predicted_sides_string}
'''
}

tier_prediction = {
    'hu': {
        1: 'Várhatóan feljebb lép, új szint: tier {tier} {emote}',
        0: 'Várhatóan ugyanezen a szinten marad: tier {tier} {emote}',
        -1: 'Várhatóan visszaesik, új szint: tier {tier} {emote}'
    },
    'en': {
        1: 'Most likely advancing to: tier {tier} {emote}',
        0: 'Most likely staying in the current tier: tier {tier} {emote}',
        -1: 'Most likely dropping to: tier {tier} {emote}'
    }
}

predicted_team = {
    'hu': "- {emote_color}{emote_house} **{main_world_name}** {linked_world_names}",
    'en': "- {emote_color}{emote_house} **{main_world_name}** {linked_world_names}"
}


def build_matchup_prediction_string(
        predicted_sides: list[MatchupSide],
        predicted_tier: int,
        predicted_result: MatchupResult,
        home_world: WvwWorld,
        locale: str
) -> str:
    """
    Create a string describing the next matchup, based on the current ones results.
    """

    tier_prediction_string = template_utils.get_localized_template(tier_prediction, locale)[predicted_result.offset]\
        .format(
            tier=str(predicted_tier),
            emote=discord_utils.default_emote(predicted_result.emote_name)
        )

    side_strings = []
    for predicted_side in predicted_sides:
        is_home_side = predicted_side.contains_world(home_world.world_id)

        linked_world_names = [linked_world.world_name for linked_world in predicted_side.linked_worlds]
        linked_world_names_joined = ', '.join(linked_world_names)

        side_string = template_utils.get_localized_template(predicted_team, locale).format(
            emote_color=discord_utils.default_emote(predicted_side.color.emote_name),
            emote_house=discord_utils.default_emote('house') if is_home_side else '',
            main_world_name=predicted_side.main_world.world_name,
            linked_world_names=linked_world_names_joined
        )
        side_strings.append(side_string)

    return template_utils.get_localized_template(matchup_prediction, locale).format(
        tier=str(predicted_tier + predicted_result.offset),
        tier_prediction_string=tier_prediction_string,
        predicted_sides_string='\n'.join(side_strings)
    )
