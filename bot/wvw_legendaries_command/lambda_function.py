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

wvw_legendary_non_armor_items = [
    item_utils.Item(81462, "Warbringer", "warbringer", 1097447840579596318),
    item_utils.Item(93105, "Conflux", "conflux", 1097447838226599947),
]

wvw_legendary_armor_ids = {
    'light': {
        'head': [82902, 82925],
        'shoulder': [83308, 82173],
        'chest': [83036, 84508],
        'glove': [84629, 82109],
        'leg': [83497, 82502],
        'foot': [83482, 83289]
    },
    'medium': {
        'head': [82180, 82437],
        'shoulder': [82994, 83087],
        'chest': [84578, 82102],
        'glove': [82552, 84110],
        'leg': [82903, 83862],
        'foot': [82093, 83699]
    },
    'heavy': {
        'head': [84176, 84301],
        'shoulder': [84181, 82963],
        'chest': [83394, 84481],
        'glove': [82456, 82348],
        'leg': [83702, 82196],
        'foot': [83094, 82801]
    }
}

armor_set_size = 6

loading_emote = discord_utils.animated_emote('loading', discord_utils.loading_emote_id)
eyes_emote = discord_utils.default_emote('eyes')

success_emote = discord_utils.default_emote('white_check_mark')
fail_emote = discord_utils.default_emote('x')


def lambda_handler(event, context):
    info = discord_utils.extract_info(event)
    monitoring.log_command(info, 'wvw_currencies')
    try:
        loading_message = template_utils.get_localized_template(templates.loading, info.locale).format(
            emote_eyes=eyes_emote,
            emote_loading=loading_emote
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, loading_message)

        api_key = gw2_user_repo.get_api_key(info.user_id)
        legendary_armory = gw2_api_interactions.get_legendary_armory(api_key)

        wvw_legendary_non_armor_amounts = item_utils.empty_amounts(wvw_legendary_non_armor_items)
        item_utils.count_amounts_in_legendary_armory(wvw_legendary_non_armor_amounts, legendary_armory)

        light_armor_set_count = count_armor_set('light', legendary_armory)
        medium_armor_set_count = count_armor_set('medium', legendary_armory)
        heavy_armor_set_count = count_armor_set('heavy', legendary_armory)

        message = compile_legendaries_message(
            non_armor_amounts=wvw_legendary_non_armor_amounts,
            light_set_size=light_armor_set_count,
            medium_set_size=medium_armor_set_count,
            heavy_set_size=heavy_armor_set_count
        )
        discord_interactions.respond_to_discord_interaction(info.interaction_token, message)
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


def count_armor_set(weight: str, legendary_armory) -> int:
    """
    Count how many legendary armor pieces are in the armory, of a given armor weight.
    """
    set_size = 0
    set_size += count_armor_piece(weight, 'head', legendary_armory)
    set_size += count_armor_piece(weight, 'shoulder', legendary_armory)
    set_size += count_armor_piece(weight, 'chest', legendary_armory)
    set_size += count_armor_piece(weight, 'glove', legendary_armory)
    set_size += count_armor_piece(weight, 'leg', legendary_armory)
    set_size += count_armor_piece(weight, 'foot', legendary_armory)
    return set_size


def count_armor_piece(weight: str, piece: str, legendary_armory) -> int:
    """
    Count how many of the specified pieces there are, from a given armor weight (for example "medium helm")
    """
    piece_ids = wvw_legendary_armor_ids[weight][piece]
    amounts = item_utils.empty_amounts(piece_ids)
    item_utils.count_amounts_in_legendary_armory(amounts, legendary_armory)
    # at most 1 weight + piece is counted. unlikely, but possible that a player has more
    return min(1, item_utils.sum_amounts(amounts))


def compile_legendaries_message(
        non_armor_amounts,
        light_set_size: int,
        medium_set_size: int,
        heavy_set_size: int,
        locale: str
) -> str:
    non_armor_details = []
    for non_armor_amount in non_armor_amounts:
        has_legendary = non_armor_amount.amount > 0
        non_armor_detail = template_utils.get_localized_template(templates.non_armor_detail, locale).format(
            legendary_name=non_armor_amount.item.item_name,
            emote_legendary=discord_utils.custom_emote(non_armor_amount.item.emote_name, non_armor_amount.item.emote_id),
            state=template_utils.get_localized_template(templates.states, locale)[has_legendary],
            emote_state=success_emote if has_legendary else fail_emote
        )
        non_armor_details.append(non_armor_detail)

    return template_utils.get_localized_template(templates.legendaries_response, locale).format(
        emote_wvw=discord_utils.custom_emote('wvw_icon', discord_utils.wvw_icon_id),
        non_armor_legendary_details='\n'.join(non_armor_details),
        light_armor_details=compile_armor_details_message('light', locale, light_set_size),
        medium_armor_details=compile_armor_details_message('medium', locale, medium_set_size),
        heavy_armor_details=compile_armor_details_message('heavy', locale, heavy_set_size)
    )


def compile_armor_details_message(weight: str, locale: str, set_size: int) -> str:
    return template_utils.get_localized_template(templates.armor_detail, locale).format(
        armor_weight=template_utils.get_localized_template(templates.armor_weights, locale)[weight],
        amount=str(set_size),
        max=armor_set_size
    )

