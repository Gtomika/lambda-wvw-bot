from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import gw2_guilds
from bot.commons import template_utils
from . import scheduled_lambda_utils
from . import templates


def handle_raid_reminder_event(
    event,
    guilds_repo: gw2_guilds.Gw2GuildRepo,
    personality: discord_interactions.WebhookPersonality,
    locale: str
):
    """
    An event where a guild raid is due soon. Posted to the guilds announcement channels. Details are in the event param.
    """
    guild_id = event['guild_id']
    raid_name = event['raid_name']
    start_time = event['raid_start_time']
    duration_hours = event['raid_duration']

    reminder_string = template_utils.get_localized_template(templates.raid_reminder, locale).format(
        event_name=raid_name,
        start_time=start_time,
        duration_hours=duration_hours
    )

    wvw_role_ids = guilds_repo.get_wvw_roles(guild_id)
    if len(wvw_role_ids) > 0:
        reminder_string += f'\n{discord_utils.mention_multiple_roles(wvw_role_ids)}'

    announcement_channels = guilds_repo.get_announcement_channels(guild_id)
    scheduled_lambda_utils.post_to_announcement_channels(
        guild_id=guild_id,
        announcement_channels=announcement_channels,
        personality=personality,
        message=reminder_string
    )
