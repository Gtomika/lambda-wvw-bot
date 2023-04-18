from bot.commons import common_exceptions


class WvwRaid:
    """
    WvW raid event representation.
    """

    def __init__(self, event_name: str, day: str, start_time: str, duration_hours: int, reminder: bool):
        """
        Attribute names are intentionally short. Additional optional attribute is schedule hash
        """
        self.name = event_name
        self.day = day
        self.time = start_time
        self.dur = duration_hours
        self.reminder = reminder

    def set_schedule_hash(self, schedule_hash: str):
        self.hash = schedule_hash


guild_id_field_name = 'GuildId'
home_world_field_name = 'HomeWorld'
announcement_channels_field_name = 'AnnouncementChannels'
manager_roles_field_name = 'ManagerRoles'
wvw_roles_field_name = 'WvwRoles'
wvw_raids_field_name = 'WvwRaids'


class Gw2GuildRepo:
    """
    Manage the DynamoDB table gw2 guilds: all info related to a guild that this bot is in.
    This table has the following structure:
    {
        "GuildId": "1234567",
        "HomeWorld": {
            "id": 1003,
            "name": "Far Shiverpeaks",
            "population": "Full"
        },
        "AnnouncementChannels": [
            {
                "id": "12345",
                "webhook": "https://..."
            },
            {
                "id": "12345",
                "webhook": "https://..."
            }
        ],
        "ManagerRoles": ["872344", "123456"],
        "WvwRoles": ["39841894", "12931931"],
        "WvwRaids": [
            {
                "name": "Morning Raid",
                "day": "monday",
                "time": "08:00",
                "dur": 2,
                "reminder": false,
                "hash: "..."
            },
            ...
        ]
    }
    Note that GuildID is the discord guild ID in this case.
    """

    def __init__(self, table_name, dynamodb_resource):
        self.gw2_guild_table = dynamodb_resource.Table(table_name)

    def find_all_guild_ids(self):
        """
        Returns all the guild ID.
        """
        response = self.gw2_guild_table.scan(ProjectionExpression=guild_id_field_name)
        return [guild[guild_id_field_name] for guild in response['Items']]

    def find_all_guilds(self, attributes):
        """
        Returns all guild IDs with the projected attributes. IDs will always be included.
        """
        attributes.append(guild_id_field_name)
        response = self.gw2_guild_table.scan(ProjectionExpression=','.join(attributes))
        return response['Items']

    def save_guild_home_world(self, guild_id: str, home_world_id: int, home_world_name: str, population: str) -> None:
        """
        Save a new home world for the selected guild. Throws:
         - ClientError: internal error
        """
        guild = self.__get_or_empty_guild(guild_id)
        guild[home_world_field_name] = {
            'id': home_world_id,
            'name': home_world_name,
            'population': population
        }
        self.__save_guild(guild)

    def delete_home_world(self, guild_id: str):
        try:
            guild = self.__get_guild(guild_id)
            if home_world_field_name in guild:
                del guild[home_world_field_name]
                self.__save_guild(guild)
        except common_exceptions.NotFoundException:
            return

    def get_guild_home_world(self, guild_id: str) -> dict:
        """
        Get selected guilds home world. Throws:
         - ClientError: internal error
         - HomeWorldNotSetException: this guild does not have home world set
        """
        try:
            guild = self.__get_guild(guild_id)
            if home_world_field_name not in guild:
                raise common_exceptions.HomeWorldNotSetException
            return guild[home_world_field_name]
        except common_exceptions.NotFoundException:
            raise common_exceptions.HomeWorldNotSetException

    def add_manager_role(self, guild_id: str, role_id: str):
        """
        Save a new role as manager role
        """
        guild = self.__get_or_empty_guild(guild_id)
        if manager_roles_field_name in guild:
            if role_id not in guild[manager_roles_field_name]:  # avoids duplication
                guild[manager_roles_field_name].append(role_id)
                self.__save_guild(guild)
        else:
            manager_roles = [role_id]
            guild[manager_roles_field_name] = manager_roles
            self.__save_guild(guild)

    def delete_manager_role(self, guild_id: str, role_id: str):
        """
        Delete a new role as manager role
        """
        try:
            guild = self.__get_guild(guild_id)
            if manager_roles_field_name in guild and role_id in guild[manager_roles_field_name]:
                guild[manager_roles_field_name].remove(role_id)
                self.__save_guild(guild)
        except common_exceptions.NotFoundException:
            return

    def get_manager_roles(self, guild_id: str):
        """
        Array of role IDs. If guild has no manager roles, empty array is returned.
        """
        try:
            guild = self.__get_guild(guild_id)
            if manager_roles_field_name in guild:
                return guild[manager_roles_field_name]
            else:
                return []
        except common_exceptions.NotFoundException:
            return []

    def add_wvw_role(self, guild_id: str, role_id: str):
        """
        Save a new role as wvw role. Returns true if the role was
        added, false if the role was already present and not added again.
        """
        guild = self.__get_or_empty_guild(guild_id)
        if wvw_roles_field_name in guild:
            if role_id not in guild[wvw_roles_field_name]: # avoids duplication
                guild[wvw_roles_field_name].append(role_id)
                self.__save_guild(guild)
        else:
            wvw_roles = [role_id]
            guild[wvw_roles_field_name] = wvw_roles
            self.__save_guild(guild)

    def delete_wvw_role(self, guild_id: str, role_id: str):
        """
        Delete a new role as wvw role
        """
        try:
            guild = self.__get_guild(guild_id)
            if wvw_roles_field_name in guild and role_id in guild[wvw_roles_field_name]:
                guild[wvw_roles_field_name].remove(role_id)
                self.__save_guild(guild)
        except common_exceptions.NotFoundException:
            return

    def get_wvw_roles(self, guild_id: str):
        """
        Array of role IDs. If guild has no wvw roles, empty array is returned.
        """
        try:
            guild = self.__get_guild(guild_id)
            if wvw_roles_field_name in guild:
                return guild[wvw_roles_field_name]
            else:
                return []
        except common_exceptions.NotFoundException:
            return []

    def put_announcement_channel(self, guild_id: str, channel_id: str, webhook_url: str):
        """
        Save a discord channel ID as announcement channel for this guild
        """
        announcement_channel_dict = {
            'id': channel_id,
            'webhook': webhook_url
        }
        guild = self.__get_or_empty_guild(guild_id)
        if announcement_channels_field_name in guild:
            if channel_id not in guild[announcement_channels_field_name]:  # avoids duplication
                guild[announcement_channels_field_name].append(announcement_channel_dict)
            else:  # need to replace, webhook possible changed
                for channel in guild[announcement_channels_field_name]:
                    if channel['id'] == channel_id:
                        channel['webhook'] = webhook_url
            self.__save_guild(guild)
        else:
            announcement_channels = [announcement_channel_dict]
            guild[announcement_channels_field_name] = announcement_channels
            self.__save_guild(guild)

    def delete_announcement_channel(self, guild_id: str, channel_id: str):
        """
        Delete an announcement channel. Previously existing webhook is returned so
        that goodbye message can be invoked (only if existed).
        """
        try:
            guild = self.__get_guild(guild_id)
            if announcement_channels_field_name in guild:
                webhook = None
                current_channels = guild[announcement_channels_field_name]
                for channel in guild[announcement_channels_field_name]:
                    if channel['id'] == channel_id:
                        webhook = channel['webhook']
                guild[announcement_channels_field_name] = [channel_data for channel_data in current_channels if channel_data['id'] != channel_id]
                self.__save_guild(guild)
                return webhook
            else:
                return None
        except common_exceptions.NotFoundException:
            return None

    def get_announcement_channels(self, guild_id: str):
        """
        Array of announcement channel IDs. If guild has no announcement channels, empty array is returned.
        """
        try:
            guild = self.__get_guild(guild_id)
            if announcement_channels_field_name in guild:
                return guild[announcement_channels_field_name]
            else:
                return []
        except common_exceptions.NotFoundException:
            return []

    def add_wvw_raid(self, guild_id: str, raid: WvwRaid):
        guild = self.__get_or_empty_guild(guild_id)
        if wvw_raids_field_name in guild:
            raids = guild[wvw_raids_field_name]
            raids.append(vars(raid))
        else:
            raids = [vars(raid)]
            guild[wvw_raids_field_name] = raids
        self.__save_guild(guild)

    def delete_wvw_raid(self, guild_id: str, raid_name: str) -> bool:
        try:
            guild = self.__get_guild(guild_id)
            if wvw_raids_field_name in guild:
                original_raids = guild[wvw_raids_field_name]
                new_raids = [raid for raid in original_raids if raid['name'] != raid_name]
                if len(original_raids) != len(new_raids):
                    guild[wvw_raids_field_name] = new_raids
                    self.__save_guild(guild)
                    return True
                return False
            else:
                return False
        except common_exceptions.NotFoundException:
            return False

    def list_wvw_raids(self, guild_id: str):
        try:
            guild = self.__get_guild(guild_id)
            if wvw_raids_field_name in guild:
                return [self.__raid_from_dict(raid_dict) for raid_dict in guild[wvw_raids_field_name]]
            else:
                return []
        except common_exceptions.NotFoundException:
            return []

    def __get_guild(self, guild_id: str):
        response = self.gw2_guild_table.get_item(Key={guild_id_field_name: guild_id})
        if 'Item' not in response:
            raise common_exceptions.NotFoundException
        return response['Item']

    def __save_guild(self, guild):
        self.gw2_guild_table.put_item(Item=guild)

    def __empty_guild(self, guild_id: str):
        return { guild_id_field_name: guild_id }

    def __get_or_empty_guild(self, guild_id: str):
        try:
            return self.__get_guild(guild_id)
        except common_exceptions.NotFoundException:
            return self.__empty_guild(guild_id)

    def __raid_from_dict(self, raid_dict) -> WvwRaid:
        """
        Convert dict extracted from dynamodb into WvW raid object.
        Should not be used on any other dict.
        """
        schedule_hash = raid_dict['hash'] if 'hash' in raid_dict else None
        return WvwRaid(raid_dict['name'], raid_dict['day'], raid_dict['time'],
                       raid_dict['dur'], raid_dict['reminder'], schedule_hash)



