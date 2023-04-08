import os
import boto3
import botocore.client

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import common_exceptions
from bot.commons import template_utils
from bot.commons import gw2_api_interactions
from bot.commons import gw2_users
from . import templates

dynamodb_resource = boto3.resource('dynamodb')
gw2_users_table_name = os.environ['GW2_USERS_TABLE_NAME']
gw2_user_repo = gw2_users.Gw2UsersRepo(gw2_users_table_name, dynamodb_resource)


def lambda_handler(event, context):
    info = discord_utils.extract_info(event)

    progress_message = template_utils.get_localized_template(templates.wvw_rank_reading, info.locale)\
        .format(emote_loading=discord_utils.animated_emote('loading', discord_utils.loading_emote_id))
    discord_interactions.respond_to_discord_interaction(info.interaction_token, progress_message)

    try:
        api_key = gw2_user_repo.get_api_key(info.user_id)
        account = gw2_api_interactions.get_account(api_key)

        commander_tag_state = 'commander' if account['commander'] else 'not_commander'  # guaranteed to be present

        if 'wvw_rank' not in account:  # required 'progression' permission on API key
            raise gw2_api_interactions.ApiKeyUnauthorizedException
        wvw_rank = account['wvw_rank']
        wvw_ranks_data = gw2_api_interactions.get_wvw_ranks()
        wvw_title = find_wvw_title(wvw_rank, wvw_ranks_data)

        home_world_id = account['world']  # guaranteed to be present
        home_world = gw2_api_interactions.get_home_world_by_id(home_world_id)['name']

        success_message = template_utils.get_localized_template(templates.wvw_rank_response, info.locale).format(
            wvw_rank=str(wvw_rank),
            wvw_title=wvw_title,
            home_world=home_world,
            emote_commander=discord_utils.custom_emote('commander', discord_utils.commander_emote_id),
            commander_tag_status=template_utils.get_localized_template(templates.commander_tag_states, info.locale)[commander_tag_state]
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, success_message)
    except common_exceptions.NotFoundException:
        template_utils.format_and_respond_api_key_required(discord_interactions, discord_utils, info)
    except gw2_api_interactions.ApiKeyUnauthorizedException:
        template_utils.format_and_respond_to_command_unauthorized(discord_interactions, discord_utils, info)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)
    except botocore.client.ClientError:
        template_utils.format_and_respond_internal_error(discord_interactions, info)


def find_wvw_title(users_wvw_rank, wvw_ranks_data):
    for wvw_rank_data in reversed(wvw_ranks_data):
        if users_wvw_rank >= wvw_rank_data['min_rank']:
            return wvw_rank_data['title']
    return 'Unknown'

