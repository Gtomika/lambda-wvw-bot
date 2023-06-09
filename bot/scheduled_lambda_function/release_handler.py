from bot.commons import gw2_guilds
from bot.commons import discord_utils
from bot.commons import discord_interactions
from bot.commons import template_utils
from . import templates
from . import scheduled_lambda_utils

announce_prefix = '[ANNOUNCE]'


def handler_release_announcement(
    event,
    guilds_repo: gw2_guilds.Gw2GuildRepo,
    personality: discord_interactions.WebhookPersonality
):
    """
    Called when a successful deployment was made. The commit message (if marked for announcement)
    will be posted on the announcement channels.
    """
    commit_message: str = event['commit_message']
    if commit_message.startswith(announce_prefix):
        trimmed_commit_message = commit_message.removeprefix(announce_prefix).strip()
        for guild in guilds_repo.find_all_guilds([
            gw2_guilds.announcement_channels_field_name,
            gw2_guilds.language_field_name
        ]):
            locale = scheduled_lambda_utils.get_guild_language_or_default(guild)
            announcement_message = template_utils.get_localized_template(templates.release_announcement, locale).format(
                emote_robot=discord_utils.default_emote('robot'),
                commit_message=trimmed_commit_message,
                emote_github=discord_utils.custom_emote('github', discord_utils.github_emote_id)
            )

            announcement_channels = scheduled_lambda_utils.get_guild_attribute_or_empty(guild, gw2_guilds.announcement_channels_field_name)
            scheduled_lambda_utils.post_to_announcement_channels(
                guild_id=scheduled_lambda_utils.get_guild_attribute_or_throw(guild, gw2_guilds.guild_id_field_name),
                announcement_channels=announcement_channels,
                message=announcement_message,
                personality=personality
            )
    else:
        print(f'The deployment with commit message "{commit_message}" was not marked for announcement, and is ignored.')
