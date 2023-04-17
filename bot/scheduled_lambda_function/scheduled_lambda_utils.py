from bot.commons import common_exceptions
from bot.commons import discord_interactions


def get_guild_attribute_or_throw(guild, attribute: str):
    """
    Throws NotFoundException if this guild has no such attribute
    """
    if attribute in guild:
        return guild[attribute]
    else:
        raise common_exceptions.NotFoundException


def get_guild_attribute_or_empty(guild, attribute):
    """
    Returns empty array if this guild has no such attribute
    """
    if attribute in guild:
        return guild[attribute]
    else:
        return []


def post_to_announcement_channels(
        guild_id: str,
        personality: discord_interactions.WebhookPersonality,
        announcement_channels,
        message: str
):
    if len(announcement_channels) == 0:
        print(f"Guild with ID {guild_id} has no announcement channels set and the WvW reset reminder will not be posted.")
        return

    for channel in announcement_channels:
        discord_interactions.create_webhook_message(
            webhook_url=channel['webhook'],
            personality=personality,
            message=message
        )