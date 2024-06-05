import os
import traceback

import boto3

from bot.commons import api_gateway_interactions as agi

ssm_client = boto3.client('ssm')

# begins and ends with a /
bot_parameters_prefix = os.getenv('BOT_PARAMETERS_PREFIX')
bot_api_token = os.getenv('BOT_API_TOKEN')


# For example a request can look like:
# {
#   "lambda_wvw_event_type": "ssm_parameter_update",
#   "api_token": "some_token",
#   "parameter_name": "world_functionality_enabled", -> do not prefix it with bot namespace and environment
#   "new_value": "false"
# }
def handle_ssm_parameter_update(request_body: dict) -> dict:
    try:
        token = request_body['api_token']
        if token != bot_api_token:
            return agi.to_api_gateway_response(401, {
                'message': 'Invalid API token'
            })

        request_parameter_name = request_body['parameter_name']
        full_parameter_name = f'{bot_parameters_prefix}{request_parameter_name}'

        new_value = request_body['new_value']

        ssm_client.put_parameter(
            Name=full_parameter_name,
            Value=new_value,
            Overwrite=True
        )

        return agi.to_api_gateway_response(200, {
            'message': 'SSM parameter updated successfully',
            'parameter_name': full_parameter_name,
            'new_value': new_value
        })
    except KeyError as e:
        traceback.print_exc()
        return agi.to_api_gateway_raw_response(400, f'Malformed request: {str(e)}')
    except Exception as e:
        traceback.print_exc()
        return agi.to_api_gateway_raw_response(500, f'Failed to update SSM parameter: {str(e)}')
