import pendulum

from bot.commons import gw2_guilds
from bot.commons import matchup_utils
from bot.commons import discord_utils
from bot.commons import discord_interactions
from bot.commons import template_utils
from . import templates
from . import scheduled_lambda_utils


def handle_wvw_reset_event(
    guilds_repo: gw2_guilds.Gw2GuildRepo,
    personality: discord_interactions.WebhookPersonality
):
    """
    An event where guilds must be notified about wvw reset. Includes relink too.
    """
    is_relink = matchup_utils.is_relink(pendulum.today().at(hour=19))  # only the day and month is important

    for guild in guilds_repo.find_all_guilds([
        gw2_guilds.announcement_channels_field_name,
        gw2_guilds.wvw_roles_field_name,
        gw2_guilds.language_field_name
    ]):
        locale = scheduled_lambda_utils.get_guild_language_or_default(guild)
        reminder_string = compile_reminder_string(is_relink, locale)

        wvw_role_ids = scheduled_lambda_utils.get_guild_attribute_or_empty(guild, gw2_guilds.wvw_roles_field_name)
        if len(wvw_role_ids) > 0:
            wvw_role_mentions = discord_utils.mention_multiple_roles(wvw_role_ids)
            personalized_reminder_string = f'{reminder_string}\n{wvw_role_mentions}'
        else:
            personalized_reminder_string = reminder_string

        announcement_channels = scheduled_lambda_utils.get_guild_attribute_or_empty(guild, gw2_guilds.announcement_channels_field_name)
        scheduled_lambda_utils.post_to_announcement_channels(
            guild_id=guild[gw2_guilds.guild_id_field_name],
            announcement_channels=announcement_channels,
            personality=personality,
            message=personalized_reminder_string
        )


def compile_reminder_string(is_relink: bool, locale: str) -> str:
    commander_emote = discord_utils.custom_emote('commander', discord_utils.commander_emote_id)
    if is_relink:
        summary_string = template_utils.get_localized_template(templates.wvw_reset_summary_relink, locale).format(
            emote_warning=discord_utils.default_emote('warning'),
            emote_commander=commander_emote
        )
    else:
        summary_string = template_utils.get_localized_template(templates.wvw_reset_summary, locale).format(
            emote_commander=commander_emote
        )

    return template_utils.get_localized_template(templates.wvw_reset_reminder, locale).format(
        emote_wvw=discord_utils.custom_emote('wvw_icon', discord_utils.wvw_icon_id),
        summary_string=summary_string
    )
