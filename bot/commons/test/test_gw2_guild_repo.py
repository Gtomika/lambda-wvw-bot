import os
import unittest
from bot.commons import gw2_guilds
from bot.commons import common_exceptions
import moto
import boto3

"""Mocked AWS Credentials for moto."""
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"
os.environ['AWS_REGION'] = "eu-central-1"

mock_guild_id = 12475414
mock_home_world = 'Piken Square'
mock_role_id = 239348


def create_guilds_table(dynamodb_resource, table_name: str):
    table = dynamodb_resource.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': gw2_guilds.guild_id_field_name, 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': gw2_guilds.guild_id_field_name, 'AttributeType': 'N'}
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5})
    table.wait_until_exists()


class TestGw2GuildRepo(unittest.TestCase):

    @moto.mock_dynamodb
    def test_create_and_get_home_world(self):
        dynamodb_resource = boto3.resource('dynamodb')
        create_guilds_table(dynamodb_resource, 'guilds')

        repo = gw2_guilds.Gw2GuildRepo(table_name='guilds', dynamodb_resource=dynamodb_resource)
        repo.save_guild_home_world(mock_guild_id, mock_home_world)

        home_world = repo.get_guild_home_world(mock_guild_id)
        self.assertEqual(mock_home_world, home_world)

    @moto.mock_dynamodb
    def test_get_home_world_does_not_exist(self):
        dynamodb_resource = boto3.resource('dynamodb')
        create_guilds_table(dynamodb_resource, 'guilds')

        repo = gw2_guilds.Gw2GuildRepo(table_name='guilds', dynamodb_resource=dynamodb_resource)
        with self.assertRaises(common_exceptions.NotFoundException):
            repo.get_guild_home_world(mock_guild_id + 123)

    @moto.mock_dynamodb
    def test_manager_role_operations(self):
        dynamodb_resource = boto3.resource('dynamodb')
        create_guilds_table(dynamodb_resource, 'guilds')
        repo = gw2_guilds.Gw2GuildRepo(table_name='guilds', dynamodb_resource=dynamodb_resource)

        manager_roles = repo.get_manager_roles(mock_guild_id)
        self.assertEqual([], manager_roles)

        added = repo.add_manager_role(mock_guild_id, mock_role_id)
        manager_roles = repo.get_manager_roles(mock_guild_id)
        self.assertTrue(added)
        self.assertEqual([mock_role_id], manager_roles)

        deleted = repo.delete_manager_role(mock_guild_id, mock_role_id)
        manager_roles = repo.get_manager_roles(mock_guild_id)
        self.assertTrue(deleted)
        self.assertEqual([], manager_roles)


if __name__ == "__main__":
    unittest.main()
