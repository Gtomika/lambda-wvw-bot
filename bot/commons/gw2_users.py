import boto3

user_id_field_name = 'UserId'
api_key_field_name = 'ApiKey'


class Gw2UsersRepo:
    """
    Manage the dynamo DB table gw2 users
    """

    def __init__(self, table_name, dynamodb_resource):
        self.table_name = table_name
        self.dynamodb_resource = dynamodb_resource
        self.gw2_users_table = self.dynamodb_resource.Table(self.table_name)

    def save_api_key(self, user_id: int, api_key: str) -> None:
        """
        Save new API key for user. Throws:
         - ClientError: internal error
        """

        response = self.gw2_users_table.get_item(Key={user_id_field_name: user_id})
        if 'Item' in response:
            # user already exists
            user = response['Item']
            user[api_key_field_name] = api_key
            self.put_user(user)
        else:
            # this user does not yet exist
            user = {
                user_id_field_name: user_id,
                api_key_field_name: api_key
            }
            self.put_user(user)

    def get_api_key(self, user_id: int):
        """
        Get API key of user. Throws:
         - ClientError: internal error
         - KeyError: if user has no API key set
        """
        response = self.gw2_users_table.get_item(Key={user_id_field_name: user_id})
        return response['Item'][api_key_field_name]

    def put_user(self, user):
        """
        Do not use in code, only internal and for tests
        """
        self.gw2_users_table.put_item(Item=user)
