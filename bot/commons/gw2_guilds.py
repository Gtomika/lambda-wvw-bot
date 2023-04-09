from bot.commons import common_exceptions


class WvwRaid:
    """
    WvW raid event representation.
    """

    def __init__(self, event_name: str, day: str, start_time: str, duration_hours: int):
        """
        Attribute names are intentionally short
        """
        self.name = event_name
        self.day = day
        self.time = start_time
        self.dur = duration_hours


def __raid_from_dict(raid_dict) -> WvwRaid:
    """
    Convert dict extracted from dynamodb into WvW raid object.
    Should not be used on any other dict.
    """
    return WvwRaid(raid_dict['name'], raid_dict['day'], raid_dict['time'], raid_dict['dur'], raid_dict['rep'])


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
        "HomeWorld": "Far Shiverpeaks",
        "AnnouncementChannels": ["12345", "123986"],
        "ManagerRoles": ["872344", "123456"],
        "WvwRoles": ["39841894", "12931931"],
        "WvwRaids": [TODO]
    }
    Note that GuildID is the discord guild ID in this case.
    """

    def __init__(self, table_name, dynamodb_resource):
        self.gw2_guild_table = dynamodb_resource.Table(table_name)

    def save_guild_home_world(self, guild_id: str, home_world_id: int) -> None:
        """
        Save a new home world for the selected guild. By World ID. Throws:
         - ClientError: internal error
        """
        guild = self.__get_or_empty_guild(guild_id)
        guild[home_world_field_name] = home_world_id
        self.__save_guild(guild)

    def get_guild_home_world(self, guild_id: str) -> int:
        """
        Get selected guilds home world. Gets world ID. Throws:
         - ClientError: internal error
         - NotFoundException: this guild does not have home world set
        """
        guild = self.__get_guild(guild_id)
        if home_world_field_name not in guild:
            raise common_exceptions.NotFoundException
        return guild[home_world_field_name]

    def add_manager_role(self, guild_id: str, role_id: str) -> bool:
        """
        Save a new role as manager role. Returns true if the role was
        added, false if the role was already present and not added again.
        """
        guild = self.__get_or_empty_guild(guild_id)
        if manager_roles_field_name in guild:
            if role_id in guild[manager_roles_field_name]:
                guild[manager_roles_field_name].append(role_id)
                self.__save_guild(guild)
                return True
            else:
                return False
        else:
            manager_roles = [role_id]
            guild[manager_roles_field_name] = manager_roles
            self.__save_guild(guild)
            return True

    def delete_manager_role(self, guild_id: str, role_id: str) -> bool:
        """
        Delete a new role as manager role. Returns true if the role was
        deleted, false if the role was not present and nothing needed deletion.
        """
        try:
            guild = self.__get_guild(guild_id)
            if manager_roles_field_name in guild and role_id in guild[manager_roles_field_name]:
                guild[manager_roles_field_name].remove(role_id)
                self.__save_guild(guild)
                return True
            else:
                return False
        except common_exceptions.NotFoundException:
            return False

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

    def add_wvw_role(self, guild_id: str, role_id: str) -> bool:
        """
        Save a new role as wvw role. Returns true if the role was
        added, false if the role was already present and not added again.
        """
        guild = self.__get_or_empty_guild(guild_id)
        if wvw_roles_field_name in guild:
            if role_id in guild[wvw_roles_field_name]:
                guild[wvw_roles_field_name].append(role_id)
                self.__save_guild(guild)
                return True
            else:
                return False
        else:
            wvw_roles = [role_id]
            guild[wvw_roles_field_name] = wvw_roles
            self.__save_guild(guild)
            return True

    def delete_wvw_role(self, guild_id: str, role_id: str) -> bool:
        """
        Delete a new role as wvw role. Returns true if the role was
        deleted, false if the role was not present and nothing needed deletion.
        """
        try:
            guild = self.__get_guild(guild_id)
            if wvw_roles_field_name in guild and role_id in guild[wvw_roles_field_name]:
                guild[wvw_roles_field_name].remove(role_id)
                self.__save_guild(guild)
                return True
            else:
                return False
        except common_exceptions.NotFoundException:
            return False

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

    def add_announcement_channel(self, guild_id: str, channel_id: str):
        """
        Save a discord channel ID as announcement channel for this guild
        """
        guild = self.__get_or_empty_guild(guild_id)
        if announcement_channels_field_name in guild:
            if channel_id in guild[announcement_channels_field_name]:
                guild[announcement_channels_field_name].append(channel_id)
                self.__save_guild(guild)
                return True
            else:
                return False
        else:
            announcement_channels = [channel_id]
            guild[announcement_channels_field_name] = announcement_channels
            self.__save_guild(guild)
            return True

    def delete_announcement_channel(self, guild_id: str, channel_id: str) -> bool:
        """
        Delete an announcement channel. Returns true if the channel was
        deleted, false if the channel was not present and nothing needed deletion.
        """
        try:
            guild = self.__get_guild(guild_id)
            if announcement_channels_field_name in guild and channel_id in guild[announcement_channels_field_name]:
                guild[announcement_channels_field_name].remove(channel_id)
                self.__save_guild(guild)
                return True
            else:
                return False
        except common_exceptions.NotFoundException:
            return False

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
                return guild[wvw_raids_field_name]
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

