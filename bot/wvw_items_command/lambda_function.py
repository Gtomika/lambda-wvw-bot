import os
import traceback
import random

import boto3

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import common_exceptions
from bot.commons import template_utils
from bot.commons import gw2_api_interactions
from bot.commons import gw2_users
from bot.commons import monitoring
from bot.commons import item_utils
from . import templates

dynamodb_resource = boto3.resource('dynamodb')
gw2_users_table_name = os.environ['GW2_USERS_TABLE_NAME']
gw2_user_repo = gw2_users.Gw2UsersRepo(gw2_users_table_name, dynamodb_resource)

wvw_items = [
    item_utils.Item(71581, "Memories of battle", "memory_of_battle", 1095760396532584688),
    item_utils.Item(93146, "Emblems of the Conqueror", "emblem_conqueror", 1095760382280335481),
    item_utils.Item(93075, "Emblems of the Avenger", "emblem_avenger", 1095760380241924176),
    item_utils.Item(81296, "Legendary Spikes", "legendary_spike", 1095760391843348480),
    item_utils.Item(19678, "Gifts of Battle", "gift_of_battle", 1095760386592079903),
    item_utils.Item(78600, 'Reward Potions', 'wvw_potion', discord_utils.reward_potion_emote_id),
    item_utils.Item(96536, 'Skirmish Chest', 'skirmish_chest', 1097236097043537920)  # this is the skirmish chest after EoD
]

loading_emote = discord_utils.animated_emote('loading', discord_utils.loading_emote_id)
eyes_emote = discord_utils.default_emote('eyes')
mag_emote = discord_utils.default_emote('mag_right')
busy_emotes = [eyes_emote, mag_emote]


def lambda_handler(event, context):
    info = discord_utils.extract_info(event)
    monitoring.log_command(info, 'wvw_currencies')
    try:
        api_key = gw2_user_repo.get_api_key(info.user_id)
        wvw_item_amounts = item_utils.empty_amounts(wvw_items)

        # check all places where the items can be
        check_bank(info, api_key, wvw_item_amounts)
        check_storage(info, api_key, wvw_item_amounts)
        check_shared_inventory(info, api_key, wvw_item_amounts)

        for character_name in gw2_api_interactions.get_character_names(api_key):
            check_character_inventory(info, api_key, wvw_item_amounts, character_name)

        items_message = compile_items_message(wvw_item_amounts, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, items_message)
    except common_exceptions.NotFoundException:
        template_utils.format_and_respond_api_key_required(discord_interactions, discord_utils, info)
    except gw2_api_interactions.ApiKeyUnauthorizedException:
        template_utils.format_and_respond_to_command_unauthorized(discord_interactions, discord_utils, info)
    except gw2_api_interactions.ApiException:
        template_utils.format_and_respond_gw2_api_error(discord_interactions, info)
    except BaseException as e:
        print(f'Error while getting WvW currencies of user {info.username}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)


def check_bank(info: discord_utils.InteractionInfo, api_key: str, wvw_item_amounts):
    loading_message = template_utils.get_localized_template(templates.loading_bank, info.locale).format(
        emote_loading=loading_emote,
        emote_mag=mag_emote
    )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

    bank_contents = gw2_api_interactions.get_bank(api_key)
    item_utils.count_amounts_in_bank(wvw_item_amounts, bank_contents)


def check_storage(info: discord_utils.InteractionInfo, api_key: str, wvw_item_amounts):
    loading_message = template_utils.get_localized_template(templates.loading_storage, info.locale).format(
        emote_loading=loading_emote,
        emote_eyes=eyes_emote
    )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

    storage_contents = gw2_api_interactions.get_material_storage(api_key)
    item_utils.count_amounts_in_material_storage(wvw_item_amounts, storage_contents)


def check_shared_inventory(info: discord_utils.InteractionInfo, api_key: str, wvw_item_amounts):
    loading_message = template_utils.get_localized_template(templates.loading_shared_inventory, info.locale).format(
        emote_loading=loading_emote
    )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

    shared_inventory = gw2_api_interactions.get_shared_inventory(api_key)
    item_utils.count_amounts_in_shared_inventory(wvw_item_amounts, shared_inventory)


def check_character_inventory(info: discord_utils.InteractionInfo, api_key: str, wvw_item_amounts, character_name: str):
    loading_message = template_utils.get_localized_template(templates.loading_character, info.locale).format(
        character_name=character_name,
        emote_loading=loading_emote,
        emote_busy=random.choice(busy_emotes)
    )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

    character_inventory = gw2_api_interactions.get_character_inventory(api_key, character_name)
    item_utils.count_amounts_in_bags(wvw_item_amounts, character_inventory)


def compile_items_message(wvw_item_amounts, locale: str) -> str:
    item_details = []
    for item_amount in wvw_item_amounts:
        item_detail = template_utils.get_localized_template(templates.item_detail, locale).format(
            item_name=item_amount.item.item_name,
            item_amount=str(item_amount.amount),
            emote_item=discord_utils.custom_emote(item_amount.item.emote_name, item_amount.item.emote_id)
        )
        item_details.append(item_detail)

    return template_utils.get_localized_template(templates.items_response, locale).format(
        emote_wvw=discord_utils.custom_emote('wvw_icon', discord_utils.wvw_icon_id),
        item_details='\n'.join(item_details),
        emote_thinking=discord_utils.default_emote('thinking')
    )
