from PIL import Image
import pathlib

from bot.commons import image_utils
from bot.commons import map_utils


lambda_source_dir = img_dir = pathlib.Path(__file__).parent.resolve().as_posix()


def draw_current_map_state(wvw_map: map_utils.WvwMap, wvw_objectives_on_map: list[map_utils.WvwObjective]) -> Image:
    """
    Create an image of the current map state. Matchup is the data from the GW2 API.
    """
    map_image = image_utils.load_image_rgba(f'{lambda_source_dir}/{wvw_map.image_path}')

    for objective in wvw_objectives_on_map:
        objective_image_path = objective.get_image_path()
        if objective_image_path is None:
            continue  # this objective has no image, skip it
        objective_image = image_utils.load_image_rgba(f'{lambda_source_dir}/{objective_image_path}')

        objective_coordinates_pixels = get_objective_draw_coordinates(
            map_image=map_image,
            wvw_map=wvw_map,
            objective_image=objective_image,
            wvw_objective=objective,
        )

        # draw the objective at the calculated coordinates
        image_utils.place_image_to_point(map_image, objective_image, objective_coordinates_pixels)

        objective_upgrade_image_path = objective.get_upgrade_image_path()
        if objective_upgrade_image_path is not None:
            # this objective is upgraded, draw the upgrade icon over it
            upgrade_image = image_utils.load_image_rgba(f'{lambda_source_dir}/{objective_upgrade_image_path}')
            image_utils.place_image_to_point(map_image, upgrade_image, objective_coordinates_pixels)

    return map_image


def get_objective_draw_coordinates(
        map_image: Image,
        wvw_map: map_utils.WvwMap,
        objective_image: Image,
        wvw_objective: map_utils.WvwObjective
) -> image_utils.Coordinate:
    """
    Determine the coordinates of the objective image on the map image. This will be in pixels on the map image.
    """
    objective_coordinates_pixels = image_utils.gw2_api_coordinates_to_pixels(  # convert to pixels on the map image
        wvw_map=wvw_map,
        map_image=map_image,
        gw2_api_objective_coordinates=wvw_objective.coordinate,
    )
    return image_utils.shift_image_from_center_point(objective_image, objective_coordinates_pixels)


# from bot.commons import gw2_api_interactions
#
# matchup = gw2_api_interactions.get_wvw_matchup_report_by_id('1-3')
# selected_map = map_utils.red_borderlands
# map_image = draw_current_map_state(wvw_map=selected_map, wvw_objectives_on_map=map_utils.get_wvw_objectives_from_map(selected_map, matchup))
# image_utils.save_image_jpg(map_image, 'current_map_state.jpg')
