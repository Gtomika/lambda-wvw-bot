import os
import traceback
import io
import uuid

import boto3
from PIL import Image

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import common_exceptions
from bot.commons import template_utils
from bot.commons import gw2_api_interactions
from bot.commons import gw2_guilds
from bot.commons import map_utils
from bot.commons import world_utils
from bot.commons import monitoring
from bot.commons import matchup_utils


from . import templates
from . import map_image_generation

dynamodb_resource = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

gw2_guilds_table_name = os.environ['GW2_GUILDS_TABLE_NAME']
repo = gw2_guilds.Gw2GuildRepo(gw2_guilds_table_name, dynamodb_resource)

app_name = os.environ['APP_NAME']
app_icon_url = os.environ['APP_ICON_URL']
assets_bucket_name = os.environ['ASSETS_BUCKET_NAME']
assets_bucket_url = os.environ['ASSETS_BUCKET_URL']
map_images_prefix = os.environ['MAP_IMAGES_PREFIX']

emote_loading = discord_utils.animated_emote('loading', discord_utils.loading_emote_id)
emote_draw = discord_utils.default_emote('pencil')


def lambda_handler(event, context):
    info = discord_utils.extract_info(event)
    monitoring.log_command(info, 'wvw_map')
    guild_id = info.guild_id
    try:
        # world is selected from either guild or event
        home_world = world_utils.identify_selected_world(guild_id, repo, event)

        # get matchup report
        loading_message = template_utils.get_localized_template(templates.matchup_loading, info.locale).format(
            emote_loading=emote_loading
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

        matchup_raw = gw2_api_interactions.get_wvw_matchup_report_of_world(home_world['id'])
        matchup = matchup_utils.parse_matchup(matchup_raw)

        selected_map_discord_name = discord_utils.extract_option(event, 'map_name')
        selected_map = map_utils.select_map(selected_map_discord_name)

        # start image processing
        loading_message = template_utils.get_localized_template(templates.drawing_image, info.locale).format(
            emote_loading=emote_loading,
            emote_draw=emote_draw
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

        wvw_objectives = map_utils.get_wvw_objectives_from_map(selected_map, matchup_raw)
        map_state_image = map_image_generation.draw_current_map_state(selected_map, wvw_objectives)

        # image is processed and uploaded to S3, response to discord
        loading_message = template_utils.get_localized_template(templates.uploading_image, info.locale).format(
            emote_loading=emote_loading
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

        map_state_image_url = upload_image_to_s3(map_state_image)

        map_dominance = map_utils.WvwMapDominance(wvw_objectives)
        message, embed = compile_response(
            world_name=home_world['name'],
            wvw_map=selected_map,
            map_dominance=map_dominance,
            map_image_url=map_state_image_url,
            map_image_width=map_state_image.width,
            map_image_height=map_state_image.height,
            matchup=matchup,
            locale=info.locale
        )
        discord_interactions.respond_to_discord_interaction(
            interaction_token=info.interaction_token,
            message=message,
            embeds=[embed]
        )
    except common_exceptions.HomeWorldNotSetException:
        template_utils.format_and_respond_home_world_not_set(discord_interactions, info)
    except common_exceptions.InvalidWorldException as e:
        template_utils.format_and_response_invalid_world(discord_interactions, info, e.world_name)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)
    except BaseException:
        print(f'Error while creating map report')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def compile_response(
        world_name: str,
        wvw_map: map_utils.WvwMap,
        map_dominance: map_utils.WvwMapDominance,
        map_image_url: str,
        map_image_width: int,
        map_image_height: int,
        matchup: matchup_utils.Matchup,
        locale: str
) -> tuple[str, dict]:
    """
    Creates and formats the response message and the map image embed.
    """
    message = template_utils.get_localized_template(templates.map_state, locale).format(
        map_name=wvw_map.readable_name,
        world_name=world_name,
        team_states=compile_team_states(map_dominance, matchup, locale),
    )
    short_description = template_utils.get_localized_template(templates.short_description, locale).format(
        map_name=wvw_map.readable_name
    )
    embed = discord_utils.create_image_embed(
        title=wvw_map.readable_name,
        description=short_description,
        image_url=map_image_url,
        author_name=app_name,
        author_icon_url=app_icon_url,
        image_width=map_image_width,
        image_height=map_image_height,
        color=wvw_map.color_code
    )
    return message, embed


def compile_team_states(
        map_dominance: map_utils.WvwMapDominance,
        matchup: matchup_utils.Matchup,
        locale: str
) -> str:
    red_state = template_utils.get_localized_template(templates.team_state, locale).format(
        emote_color=discord_utils.default_emote('red_circle'),
        main_world_name=matchup.get_main_world_of_team(matchup_utils.red).world_name,
        linked_world_names=linked_worlds_string(matchup, matchup_utils.red),
        percentage=str(map_dominance.red_percentage),
        points=str(map_dominance.red_ppt)
    )

    blue_state = template_utils.get_localized_template(templates.team_state, locale).format(
        emote_color=discord_utils.default_emote('blue_circle'),
        main_world_name=matchup.get_main_world_of_team(matchup_utils.blue).world_name,
        linked_world_names=linked_worlds_string(matchup, matchup_utils.blue),
        percentage=str(map_dominance.blue_percentage),
        points=str(map_dominance.blue_ppt)
    )

    green_state = template_utils.get_localized_template(templates.team_state, locale).format(
        emote_color=discord_utils.default_emote('green_circle'),
        main_world_name=matchup.get_main_world_of_team(matchup_utils.green).world_name,
        linked_world_names=linked_worlds_string(matchup, matchup_utils.green),
        percentage=str(map_dominance.green_percentage),
        points=str(map_dominance.green_ppt)
    )

    return '\n'.join([red_state, blue_state, green_state])


def linked_worlds_string(matchup: matchup_utils.Matchup, color: matchup_utils.Color) -> str:
    world_names = [world.world_name for world in matchup.get_linked_worlds_of_team(color)]
    joined_world_names = ', '.join(world_names)
    if len(joined_world_names) > 0:
        joined_world_names = f', {joined_world_names}'
    return joined_world_names


def upload_image_to_s3(image: Image) -> str:
    """
    Uploads the map image to the assets bucket, with the appropriate prefix.
    Full URL to the newly uploaded image is returned. Cleanup of old map images
    is performed by S3 lifecycle management.
    """
    in_mem_file = image_to_in_memory_file(image)
    key = f'{map_images_prefix}{str(uuid.uuid4())}.jpg'
    s3_client.upload_fileobj(
        in_mem_file,
        assets_bucket_name,
        key
    )
    return f'{assets_bucket_url}/{key}'


def image_to_in_memory_file(image: Image) -> io.BytesIO:
    in_mem_file = io.BytesIO()
    image = image.convert('RGB')
    image.save(in_mem_file, format='JPEG')
    in_mem_file.seek(0)
    return in_mem_file
