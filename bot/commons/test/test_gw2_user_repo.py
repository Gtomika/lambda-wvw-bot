import unittest
import moto
import boto3
import os

import gw2_users

"""Mocked AWS Credentials for moto."""
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"
os.environ['AWS_REGION'] = "eu-central-1"

mock_user_id = 12475414
mock_api_key = "ABCDEFGH"


def create_users_table(dynamodb_resource, table_name: str):
    table = dynamodb_resource.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': gw2_users.user_id_field_name, 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': gw2_users.user_id_field_name, 'AttributeType': 'N'}
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5})
    table.wait_until_exists()


class TestGw2UserRepo(unittest.TestCase):

    @moto.mock_dynamodb
    def test_update_and_get_api_key_when_user_exists(self):
        dynamodb_resource = boto3.resource('dynamodb')
        create_users_table(dynamodb_resource, table_name='users')

        repo = gw2_users.Gw2UsersRepo(table_name='users', dynamodb_resource=dynamodb_resource)
        repo._Gw2UsersRepo__save_user({  # user already exists
            gw2_users.user_id_field_name: mock_user_id,
            gw2_users.api_key_field_name: mock_api_key + "ABCD"  # some other key already exists
        })

        repo.save_api_key(user_id=mock_user_id, api_key=mock_api_key)

        returned_api_key = repo.get_api_key(user_id=mock_user_id)
        self.assertEqual(mock_api_key, returned_api_key)

    @moto.mock_dynamodb
    def test_update_and_get_api_key_when_user_does_not_exists(self):
        dynamodb_resource = boto3.resource('dynamodb')
        create_users_table(dynamodb_resource, table_name='users')

        repo = gw2_users.Gw2UsersRepo(table_name='users', dynamodb_resource=dynamodb_resource)
        # this user does not yet exist
        repo.save_api_key(user_id=mock_user_id, api_key=mock_api_key)

        returned_api_key = repo.get_api_key(user_id=mock_user_id)
        self.assertEqual(mock_api_key, returned_api_key)


if __name__ == "__main__":
    unittest.main()
