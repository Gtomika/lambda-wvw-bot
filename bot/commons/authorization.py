from bot.commons import gw2_guilds
from bot.commons import discord_utils
from bot.commons import common_exceptions


class CommandAuthorizer:
    """
    This class checks that those who invoked a command from a guild
    have the right to do so.
    """

    def __init__(self, repo: gw2_guilds.Gw2GuildRepo):
        self.repo = repo

    def authorize_command(self, guild_id: str, event):
        """
        Throws: UnauthorizedException
        """
        # not from guild: private messages not authorized
        if not discord_utils.is_from_guild(event):
            return
        # admin: always allowed
        if discord_utils.is_admin(event):
            return

        # not admin: must compare guilds manager roles with members roles
        member_roles = discord_utils.extract_member_roles(event)
        guild_manager_roles = self.repo.get_manager_roles(guild_id)

        for member_role in member_roles:
            if member_role in guild_manager_roles:
                return
        raise common_exceptions.UserUnauthorizedException
