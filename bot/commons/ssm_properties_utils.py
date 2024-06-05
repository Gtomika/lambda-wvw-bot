import os

import boto3

ssm_client = boto3.client('ssm')

bot_parameters_prefix = os.getenv('BOT_PARAMETERS_PREFIX')
world_functionality_enabled_parameter_name = f'{bot_parameters_prefix}world_functionality_enabled'


def get_parameter(parameter_name: str) -> str:
    response = ssm_client.get_parameter(Name=parameter_name)
    return response['Parameter']['Value']


def get_boolean_parameter(parameter_name: str) -> bool:
    return get_parameter(parameter_name).lower() == 'true'


def is_world_functionality_enabled() -> bool:
    return get_boolean_parameter(world_functionality_enabled_parameter_name)
