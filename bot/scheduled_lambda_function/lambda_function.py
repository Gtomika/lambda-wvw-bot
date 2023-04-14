import os
import boto3

from bot.commons import gw2_guilds
from bot.commons import gw2_users

dynamodb_resource = boto3.resource('dynamodb')

gw2_guilds_table_name = os.environ['GW2_GUILDS_TABLE_NAME']
guilds_repo = gw2_guilds.Gw2GuildRepo(table_name=gw2_guilds_table_name, dynamodb_resource=dynamodb_resource)

gw2_users_table_name = os.environ['GW2_USERS_TABLE_NAME']
users_repo = gw2_users.Gw2UsersRepo(table_name=gw2_users_table_name, dynamodb_resource=dynamodb_resource)


def lambda_handler(event, context):
    """
    The "scheduled" lambda: all scheduler actions trigger this lambda with different event types
    """
    event_type = event['lambda_wvw_event_type']
    if event_type == 'wvw_reset':
        handle_wvw_reset_event()
    elif event_type == 'raid_reminder':
        handle_raid_reminder_event(event)
    elif event_type == 'home_world_population_recheck':
        handle_home_world_population_recheck()


def handle_wvw_reset_event():
    """
    An event where guilds must be notified about wvw reset. Includes relink too.
    """
    pass


def handle_raid_reminder_event(event):
    """
    An event where a guild raid is due soon. Posted to the guilds announcement channels. Details are in the event param.
    """
    pass


def handle_home_world_population_recheck():
    """
    An event where guilds home worlds must be re-checked in case their population has changed.
    Notification is sent if the population was changed.
    """
    pass
