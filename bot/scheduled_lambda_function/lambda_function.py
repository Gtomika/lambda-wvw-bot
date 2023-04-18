import os
import boto3
import traceback

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

locale = 'hu'  # TODO find a way to use the appropriate locale

app_name = os.environ['APP_NAME']
app_icon = os.environ['APP_ICON_URL']

personality = discord_interactions.WebhookPersonality(
    bot_name=app_name,
    bot_icon_url=app_icon
)


def lambda_handler(event, context):
    """
    The "scheduled" lambda: all scheduler actions trigger this lambda with different event types
    """
    event_type = event['lambda_wvw_event_type']
    try:
        if event_type == 'wvw_reset':
            wvw_reset_handler.handle_wvw_reset_event(guilds_repo, personality, locale)
        elif event_type == 'raid_reminder':
            raid_reminder_handler.handle_raid_reminder_event(event, guilds_repo, personality, locale)
        elif event_type == 'home_world_population_recheck':
            population_check_handler.handle_home_world_population_recheck(guilds_repo, personality, locale)
        elif event_type == 'release':
            release_handler.handler_release_announcement(guilds_repo, personality, locale)
        else:
            print(f'Cannot handle event because event type is unknown: {event_type}')
    except BaseException as e:
        print(f'Failed to handle event with type {event_type} due to unexpected error')
        traceback.print_exc()







