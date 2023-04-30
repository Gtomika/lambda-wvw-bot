import os
import boto3
import traceback
import json

from bot.commons import gw2_guilds
from bot.commons import gw2_users
from bot.commons import discord_interactions

from . import wvw_reset_handler
from . import population_check_handler
from . import raid_reminder_handler
from . import release_handler

dynamodb_resource = boto3.resource('dynamodb')

gw2_guilds_table_name = os.environ['GW2_GUILDS_TABLE_NAME']
guilds_repo = gw2_guilds.Gw2GuildRepo(table_name=gw2_guilds_table_name, dynamodb_resource=dynamodb_resource)

gw2_users_table_name = os.environ['GW2_USERS_TABLE_NAME']
users_repo = gw2_users.Gw2UsersRepo(table_name=gw2_users_table_name, dynamodb_resource=dynamodb_resource)

app_name = os.environ['APP_NAME']
app_icon = os.environ['APP_ICON_URL']

personality = discord_interactions.WebhookPersonality(
    bot_name=app_name,
    bot_icon_url=app_icon
)

event_type_key = 'lambda_wvw_event_type'


def lambda_handler(event, context):
    """
    The "scheduled" lambda: all scheduler actions trigger this lambda with different event types
    """
    event_type = 'unknown'
    try:
        payload = extract_event_payload(event)
        event_type = extract_event_type(payload)
        if event_type == 'wvw_reset':
            wvw_reset_handler.handle_wvw_reset_event(guilds_repo, personality)
        elif event_type == 'raid_reminder':
            raid_reminder_handler.handle_raid_reminder_event(event, guilds_repo, personality)
        elif event_type == 'home_world_population_recheck':
            population_check_handler.handle_home_world_population_recheck(guilds_repo, personality)
        elif event_type == 'release':
            release_handler.handler_release_announcement(event, guilds_repo, personality)
        elif event_type == 'test':
            print('Test event, ignoring...')
            return payload, event_type
        else:
            print(f'Cannot handle event because event type is unknown: {event_type}')
    except BaseException as e:
        print(f'Failed to handle event with type {event_type} due to unexpected error. Event body follows:')
        print(json.dumps(event))
        traceback.print_exc()


def extract_event_payload(event: dict) -> dict:
    """
    The event payload may be at a different spot depending on if this event was provisioned from
    Python SDK, or with Terraform.
    """
    if event_type_key in event:
        return event  # payload is the root event, already parsed
    elif 'Payload' in event:
        payload: str = event['Payload']
        return json.loads(payload)
    else:
        print(f'Event is in an unsupported format, cannot extract payload! Event: {json.dumps(event)}')
        raise Exception


def extract_event_type(payload: dict) -> str:
    if event_type_key in payload:
        return payload[event_type_key]
    else:
        print(f'Key {event_type_key} is not present in payload, cannot extract event type! Payload: {json.dumps(payload)}')






