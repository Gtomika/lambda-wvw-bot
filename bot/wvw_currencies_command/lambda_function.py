import os
import traceback

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

wvw_currencies = [
    item_utils.Item(15, "Badges of Honor", "badge_of_honor", 1095760372297900102),
    item_utils.Item(26, "Skirmish Claim Tickets", "skirmish_claim_ticket", 1095760400592683038),
    item_utils.Item(31, "Proofs of Heroics", "heroics", 1095760388928311377),
    item_utils.Item(36, "Proofs of Desert Heroics", "desert_heroics", 1095760377188454440),
    item_utils.Item(65, "Proofs of Jade Heroics", "jade_heroics", 1095760390153052162)
]


def lambda_handler(event, context):
    info = discord_utils.extract_info(event)
    monitoring.log_command(info, 'wvw_currencies')

    progress_message = template_utils.get_localized_template(templates.loading, info.locale)\
        .format(emote_loading=discord_utils.animated_emote('loading', discord_utils.loading_emote_id))
    discord_interactions.respond_to_discord_interaction(info.interaction_token, progress_message)

    try:
        api_key = gw2_user_repo.get_api_key(info.user_id)
        wallet = gw2_api_interactions.get_wallet(api_key)

        wvw_currencies_amounts = item_utils.empty_amounts(wvw_currencies)
        item_utils.count_amounts_in_wallet(wvw_currencies_amounts, wallet)

        currencies_response = compile_currencies_message(wvw_currencies_amounts, info.locale)
        discord_interactions.respond_to_discord_interaction(info.interaction_token, currencies_response)
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


def compile_currencies_message(wvw_currencies_amounts, locale) -> str:
    currency_details = []
    for currency in wvw_currencies_amounts:
        currency_detail = template_utils.get_localized_template(templates.currency_detail, locale).format(
            currency_name=currency.item.item_name,
            currency_amount=str(currency.amount),
            emote_currency=discord_utils.custom_emote(currency.item.emote_name, currency.item.emote_id)
        )
        currency_details.append(currency_detail)

    return template_utils.get_localized_template(templates.currencies_response, locale).format(
        emote_wvw=discord_utils.custom_emote('wvw_icon', discord_utils.wvw_icon_id),
        currency_details='\n'.join(currency_details)
    )
