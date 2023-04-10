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

mock_guild_id = "12475414"
mock_home_world_id = 1001
mock_home_world_name = 'Dzagonur [DE]'
mock_home_world_population = 'Medium'
mock_role_id = "239348"
mock_channel_id = "3857173"
mock_webhook_url = "https://discord.webhook.com/xc/abc"


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


class TestGw2GuildRepo(unittest.TestCase):

    @moto.mock_dynamodb
    def test_create_and_get_home_world(self):
        dynamodb_resource = boto3.resource('dynamodb')
        create_guilds_table(dynamodb_resource, 'guilds')

        repo = gw2_guilds.Gw2GuildRepo(table_name='guilds', dynamodb_resource=dynamodb_resource)
        repo.save_guild_home_world(mock_guild_id, mock_home_world_id, mock_home_world_name, mock_home_world_population)

        home_world = repo.get_guild_home_world(mock_guild_id)
        self.assertEqual({
            'id': mock_home_world_id,
            'name': mock_home_world_name,
            'population': mock_home_world_population
        }, home_world)

    @moto.mock_dynamodb
    def test_get_home_world_does_not_exist(self):
        dynamodb_resource = boto3.resource('dynamodb')
        create_guilds_table(dynamodb_resource, 'guilds')

        repo = gw2_guilds.Gw2GuildRepo(table_name='guilds', dynamodb_resource=dynamodb_resource)
        with self.assertRaises(common_exceptions.NotFoundException):
            repo.get_guild_home_world("1237546")

    @moto.mock_dynamodb
    def test_manager_role_operations(self):
        dynamodb_resource = boto3.resource('dynamodb')
        create_guilds_table(dynamodb_resource, 'guilds')
        repo = gw2_guilds.Gw2GuildRepo(table_name='guilds', dynamodb_resource=dynamodb_resource)

        manager_roles = repo.get_manager_roles(mock_guild_id)
        self.assertEqual([], manager_roles)

        repo.add_manager_role(mock_guild_id, mock_role_id)
        manager_roles = repo.get_manager_roles(mock_guild_id)
        self.assertEqual([mock_role_id], manager_roles)

        repo.delete_manager_role(mock_guild_id, mock_role_id)
        manager_roles = repo.get_manager_roles(mock_guild_id)
        self.assertEqual([], manager_roles)

    @moto.mock_dynamodb
    def test_wvw_role_operations(self):
        dynamodb_resource = boto3.resource('dynamodb')
        create_guilds_table(dynamodb_resource, 'guilds')
        repo = gw2_guilds.Gw2GuildRepo(table_name='guilds', dynamodb_resource=dynamodb_resource)

        wvw_roles = repo.get_wvw_roles(mock_guild_id)
        self.assertEqual([], wvw_roles)

        repo.add_wvw_role(mock_guild_id, mock_role_id)
        wvw_roles = repo.get_wvw_roles(mock_guild_id)
        self.assertEqual([mock_role_id], wvw_roles)

        repo.delete_wvw_role(mock_guild_id, mock_role_id)
        wvw_roles = repo.get_wvw_roles(mock_guild_id)
        self.assertEqual([], wvw_roles)

    @moto.mock_dynamodb
    def test_announcement_channel_operations(self):
        dynamodb_resource = boto3.resource('dynamodb')
        create_guilds_table(dynamodb_resource, 'guilds')
        repo = gw2_guilds.Gw2GuildRepo(table_name='guilds', dynamodb_resource=dynamodb_resource)

        channels = repo.get_announcement_channels(mock_guild_id)
        self.assertEqual([], channels)

        repo.add_announcement_channel(mock_guild_id, mock_channel_id, mock_webhook_url)
        channels = repo.get_announcement_channels(mock_guild_id)
        self.assertEqual([{
            'id': mock_channel_id,
            'webhook': mock_webhook_url
        }], channels)

        repo.delete_announcement_channel(mock_guild_id, mock_channel_id)
        channels = repo.get_announcement_channels(mock_guild_id)
        self.assertEqual([], channels)


if __name__ == "__main__":
    unittest.main()
