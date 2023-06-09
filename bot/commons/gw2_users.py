from bot.commons import common_exceptions

user_id_field_name = 'UserId'
api_key_field_name = 'ApiKey'


class Gw2UsersRepo:
    """
    Manage the dynamo DB table gw2 users. This table has the following format:
    {
        "UserId": 123457677,
        "ApiKey": "ABC-123"
    }
    """

    def __init__(self, table_name, dynamodb_resource):
        self.gw2_users_table = dynamodb_resource.Table(table_name)

    def save_api_key(self, user_id: str, api_key: str) -> None:
        """
        Save new API key for user. Throws:
         - ClientError: internal error
        """
        try:
            user = self.__get_user(user_id)
        except common_exceptions.NotFoundException:
            user = self.__empty_user(user_id)
        user[api_key_field_name] = api_key
        self.__save_user(user)

    def get_api_key(self, user_id: str):
        """
        Get API key of user. Throws:
         - ClientError: internal error
         - NotFoundError: if user has no API key set
        """
        response = self.gw2_users_table.get_item(Key={user_id_field_name: user_id})
        if 'Item' in response:
            item = response['Item']
            if api_key_field_name in item:
                return item[api_key_field_name]
            else:
                raise common_exceptions.NotFoundException
        else:
            raise common_exceptions.NotFoundException

    def delete_api_key(self, user_id: str):
        """
        Delete API key of user. Nothing happens if this user does not exist or has no key.
        """
        try:
            user = self.__get_user(user_id)
            if api_key_field_name not in user:
                return
            del user[api_key_field_name]
            self.__save_user(user)
        except common_exceptions.NotFoundException:
            return

    def __empty_user(self, user_id: str):
        return {user_id_field_name: user_id}

    def __save_user(self, user):
        """
        Do not use in code, only internal and for tests
        """
        self.gw2_users_table.put_item(Item=user)

    def __get_user(self, user_id: str):
        response = self.gw2_users_table.get_item(Key={user_id_field_name: user_id})
        if 'Item' not in response:
            raise common_exceptions.NotFoundException
        return response['Item']