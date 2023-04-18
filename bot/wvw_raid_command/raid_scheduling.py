import boto3
import os
import json
import pendulum

from bot.commons import time_utils
from bot.commons import template_utils

scheduler = boto3.client('scheduler')

schedule_group_name = os.environ['SCHEDULE_GROUP_NAME']
scheduler_role_arn = os.environ['SCHEDULE_ROLE_ARN']
scheduled_lambda_arn = os.environ['SCHEDULED_LAMBDA_ARN']
scheduler_target_type_arn = 'arn:aws:scheduler:::aws-sdk:lambda:invoke'

app_name = os.environ['APP_NAME']
environment = os.environ['ENVIRONMENT']
region = os.environ['AWS_REGION']


def create_schedule(guild_id: str, raid, locale: str) -> str:
    """
    Create a new AWS scheduler schedule that triggers the event reminder. Returns the
    scheduler hash, that must be stored for this event.
    """
    schedule_hash = __schedule_hash(guild_id, raid.name)
    schedule_name = __build_schedule_name(schedule_hash)

    scheduler.create_schedule(
        Name=schedule_name,
        GroupName=schedule_group_name,
        ScheduleExpression=f'cron({__build_reminder_cron(raid)})',
        FlexibleTimeWindow={
            'Mode': 'OFF'
        },
        Target=__build_schedule_target(guild_id, raid),
        ScheduleExpressionTimezone=template_utils.get_localized_template(time_utils.locale_time_zones, locale),
        Description=f'Raid reminder schedule for the guild with ID {guild_id} and event with name {raid.name}'
    )
    # individual schedules cannot be tagged, only groups
    print(f'A new EventBridge Schedule was created: {schedule_name}. It reminds about the raid {raid.name} of guild with ID {guild_id}')
    return schedule_hash


def delete_schedule(schedule_hash: str):
    schedule_name = __build_schedule_name(schedule_hash)
    scheduler.delete_schedule(
        Name=schedule_name,
        GroupName=schedule_group_name
    )
    print(f'The EventBridge schedule was deleted: {schedule_name}. It was a raid reminder.')


def __schedule_hash(guild_id: str, event_name: str) -> str:
    schedule_hash = hash(f'{guild_id}{event_name}')
    return str(abs(schedule_hash))


def __build_schedule_name(schedule_hash: str) -> str:
    # guild ID + raid name is a unique combination
    return f'{schedule_hash}-{app_name}-{environment}-{region}'


def __build_reminder_cron(raid) -> str:
    start_time = pendulum.parse(raid.time)
    day = cron_day_mappings[raid.day]
    return f'{str(start_time.minute)} {str(start_time.hour)} ? * {day} *'


cron_day_mappings = {
    'monday': 'MON',
    'tuesday': 'TUE',
    'wednesday': 'WED',
    'thursday': 'THU',
    'friday': 'FRI',
    'saturday': 'SAT',
    'sunday': 'SUN',
    'every_day': '*'
}


def __build_schedule_target(guild_id: str, raid) -> dict:
    return {
        'RoleArn': scheduler_role_arn,
        'Arn': scheduler_target_type_arn,
        'Input': json.dumps({
            'FunctionName': scheduled_lambda_arn,
            'InvocationType': 'Event',
            'Payload': json.dumps({  # the schedule is triggered 30 minutes before the raid
                'lambda_wvw_event_type': 'raid_reminder',
                'guild_id': guild_id,
                'raid_name': raid.name,
                'raid_start_time': raid.time,
                'raid_duration': raid.dur
            })
        })
    }
