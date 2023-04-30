import unittest.mock
from unittest import TestCase
import json
import os
import boto3
import moto
import io
import zipfile

import discord_utils


mock_ack_interaction = """
{
    "type": 1
}
"""

mock_info_interaction = """
{
    "type": 2,
    "token": "A_UNIQUE_TOKEN",
    "member": {
        "user": {
            "id": "53908232506183680",
            "username": "Mason",
            "avatar": "a_d5efa99b3eeaa7dd43acca82f5692432",
            "discriminator": "1337",
            "public_flags": 131141
        },
        "roles": ["539082325061836999"],
        "premium_since": null,
        "permissions": "2147483647",
        "pending": false,
        "nick": null,
        "mute": false,
        "joined_at": "2017-03-13T19:19:14.040000+00:00",
        "is_pending": false,
        "deaf": false
    },
    "id": "786008729715212338",
    "guild_id": "290926798626357999",
    "app_permissions": "442368",
    "guild_locale": "en-US",
    "locale": "en-US",
    "data": {
        "options": [],
        "type": 1,
        "name": "lambda_info",
        "id": "771825006014889984"
    },
    "channel_id": "645027906669510667"
}
"""

mock_architecture_interaction = """
{
    "type": 2,
    "token": "A_UNIQUE_TOKEN",
    "member": {
        "user": {
            "id": "53908232506183680",
            "username": "Mason",
            "avatar": "a_d5efa99b3eeaa7dd43acca82f5692432",
            "discriminator": "1337",
            "public_flags": 131141
        },
        "roles": ["539082325061836999"],
        "premium_since": null,
        "permissions": "2147483647",
        "pending": false,
        "nick": null,
        "mute": false,
        "joined_at": "2017-03-13T19:19:14.040000+00:00",
        "is_pending": false,
        "deaf": false
    },
    "id": "786008729715212338",
    "guild_id": "290926798626357999",
    "app_permissions": "442368",
    "guild_locale": "en-US",
    "locale": "en-US",
    "data": {
        "options": [{
            "type": 3,
            "name": "architecture",
            "value": "traditional"
        }],
        "type": 1,
        "name": "architecture_choice",
        "id": "771825006014889984"
    },
    "channel_id": "645027906669510667"
}
"""


class DiscordInteractionLambdaTest(TestCase):

    @classmethod
    def setUpClass(cls):
        mock_aws_credentials()

        cls.mock_lambda = moto.mock_lambda()
        cls.mock_lambda.start()

        info_arn = mock_create_lambda('LambdaInfoCommandLambda')
        archi_arn = mock_create_lambda('ArchitectureChoiceLambda')

        os.environ['APPLICATION_PUBLIC_KEY'] = 'aa66cd8542274a1ae6ed42d4214ab7f7dfc5d85fc4fc50e1596119860222dc81'
        commands_data = json.dumps([
            {
                'command_name_discord': 'lambda_info',
                'command_lambda_arn': info_arn
            },
            {
                'command_name_discord': 'architecture_choice',
                'command_lambda_arn': archi_arn
            }
        ])
        os.environ['COMMANDS'] = commands_data

    @unittest.mock.patch(
        'lambda_function.is_request_verified')
    def test_unverified_interaction(self, mock_verify_check):
        mock_verify_check.return_value = False

        # importing here simulates AWS lambda loading this file
        from lambda_function import lambda_handler
        response = lambda_handler({
            'headers': {},
            'body': mock_info_interaction
        }, {})

        self.assertEqual(401, response['statusCode'])

    @unittest.mock.patch(
        'lambda_function.is_request_verified')
    def test_ack_interaction(self, mock_verify_check):
        mock_verify_check.return_value = True

        # importing here simulates AWS lambda loading this file
        from lambda_function import lambda_handler
        response = lambda_handler({
            'headers': {},
            'body': mock_ack_interaction
        }, {})

        self.assertEqual(200, response['statusCode'])
        body = json.loads(response['body'])
        self.assertEqual(discord_utils.ACK_TYPE, body['type'])

    @unittest.mock.patch(
        'lambda_function.is_request_verified')
    def test_forward_info_interaction(self, mock_verify_check):
        mock_verify_check.return_value = True

        # importing here simulates AWS lambda loading this file
        from lambda_function import lambda_handler
        response = lambda_handler({
            'headers': {},
            'body': mock_info_interaction
        }, {})

        self.assertEqual(200, response['statusCode'])
        body = json.loads(response['body'])
        self.assertEqual(discord_utils.DEFER_TYPE, body['type'])

    @unittest.mock.patch(
        'lambda_function.is_request_verified')
    def test_forward_architecture_interaction(self, mock_verify_check):
        mock_verify_check.return_value = True

        # importing here simulates AWS lambda loading this file
        from lambda_function import lambda_handler
        response = lambda_handler({
            'headers': {},
            'body': mock_architecture_interaction
        }, {})

        self.assertEqual(200, response['statusCode'])
        body = json.loads(response['body'])
        self.assertEqual(discord_utils.DEFER_TYPE, body['type'])

    @classmethod
    def tearDownClass(cls) -> None:
        cls.mock_lambda.stop()


def mock_aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"
    os.environ['AWS_REGION'] = "eu-central-1"


def mock_create_lambda(function_name: str) -> str:
    conn = boto3.client('lambda')
    response = conn.create_function(
        FunctionName=function_name,
        Runtime='python3.9',
        Role=get_mock_role_arn(),
        Handler='lambda_function.lambda_handler',
        Code={
            'ZipFile': get_test_zip_file(),
        },
        Description='test lambda function',
        Timeout=3,
        MemorySize=128,
        Publish=True
    )
    return response['FunctionName']


def get_test_zip_file():
    # actual contents of this are not important
    pfunc = '''
    import json
    def lambda_handler(event, context):
        resp = {"value":"input_str"}
        return json.dumps(resp)
    '''
    zip_output = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED)
    zip_file.writestr('lambda_function.py', pfunc)
    zip_file.close()
    zip_output.seek(0)
    return zip_output.read()


def get_mock_role_arn() -> str:
    with moto.mock_iam():
        iam = boto3.client("iam")
        return iam.create_role(
            RoleName="my-role",
            AssumeRolePolicyDocument="some policy",
            Path="/my-path/",
        )["Role"]["Arn"]


if __name__ == '__main__':
    unittest.main()
