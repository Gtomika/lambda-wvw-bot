import json
import unittest
import os

import boto3
import moto

import gw2_guilds
import gw2_users

"""Mocked AWS Credentials for moto."""
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"
os.environ['AWS_REGION'] = "eu-central-1"

event_type_key = 'lambda_wvw_event_type'


def create_guilds_table(dynamodb_resource, table_name: str):
    table = dynamodb_resource.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': gw2_guilds.guild_id_field_name, 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': gw2_guilds.guild_id_field_name, 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5})
    table.wait_until_exists()


def create_users_table(dynamodb_resource, table_name: str):
    table = dynamodb_resource.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': gw2_users.user_id_field_name, 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': gw2_users.user_id_field_name, 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5})
    table.wait_until_exists()


os.environ['GW2_GUILDS_TABLE_NAME'] = 'guilds'
os.environ['GW2_USERS_TABLE_NAME'] = 'users'
os.environ['APP_NAME'] = 'Test'
os.environ['APP_ICON_URL'] = 'Test'


class TestScheduledLambda(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.mock_dynamodb = moto.mock_dynamodb()
        cls.mock_dynamodb.start()

        dynamodb_resource = boto3.resource('dynamodb')
        create_guilds_table(dynamodb_resource, 'guilds')
        create_users_table(dynamodb_resource, 'users')

    def test_scheduled_event_python_sdk_type(self):
        python_sdk_event = {
            event_type_key: 'test',
            'some_data': 'nice'
        }

        # simulating AWS lambda loading the file
        from bot.scheduled_lambda_function.lambda_function import lambda_handler

        payload, event_type = lambda_handler(python_sdk_event, None)

        self.assertEqual(python_sdk_event, payload)
        self.assertEqual('test', event_type)

    def test_scheduled_event_terraform_type(self):
        terraform_payload = {
            event_type_key: 'test',
            'some_data': 'nice'
        }
        terraform_event = {
            "FunctionName": "arn:aws:lambda:eu-central-1:844933496707:function:LambdaWvwBot-Scheduled-prd-eu-central-1",
            "InvocationType": "Event",
            "Payload": json.dumps(terraform_payload)
        }

        # simulating AWS lambda loading the file
        from bot.scheduled_lambda_function.lambda_function import lambda_handler

        payload, event_type = lambda_handler(terraform_event, None)

        self.assertEqual(terraform_payload, payload)
        self.assertEqual('test', event_type)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.mock_dynamodb.stop()