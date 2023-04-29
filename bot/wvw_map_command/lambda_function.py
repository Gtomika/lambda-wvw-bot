import os
import traceback

import boto3

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import common_exceptions
from bot.commons import template_utils
from bot.commons import gw2_api_interactions
from bot.commons import gw2_guilds
from bot.commons import matchup_utils
from bot.commons import world_utils
from bot.commons import monitoring
from . import templates

dynamodb_resource = boto3.resource('dynamodb')
gw2_guilds_table_name = os.environ['GW2_GUILDS_TABLE_NAME']
repo = gw2_guilds.Gw2GuildRepo(gw2_guilds_table_name, dynamodb_resource)


def lambda_handler(event, context):
    info = discord_utils.extract_info(event)
    monitoring.log_command(info, 'wvw_map')
    guild_id = info.guild_id
    try:
        discord_interactions.respond_to_discord_interaction(info.interaction_token, 'Command not yet implemented')
    except common_exceptions.HomeWorldNotSetException:
        template_utils.format_and_respond_home_world_not_set(discord_interactions, info)
    except common_exceptions.InvalidWorldException as e:
        template_utils.format_and_response_invalid_world(discord_interactions, info, e.world_name)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)
    except BaseException:
        print(f'Error while create map report')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)