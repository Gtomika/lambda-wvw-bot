from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import template_utils
import templates


discord_developer_id = 416289572289249280
documentation_url = 'https://gtomika.github.io/mod-wvw-bot/'  # TODO update this


def lambda_handler(event, context):
    """
    Handler for the 'help' slash command
    """
    info = discord_utils.InteractionInfo(event)

    response_template = template_utils.get_localized_template(
        template_map=templates.help_response_template,
        locale=info.locale
    )
    message = response_template.format(
        developer=discord_utils.mention_user(discord_developer_id),
        emote_docu=discord_utils.default_emote('bookmark_tabs'),
        docu_url=f'<{documentation_url}>',  # <> symbols disable preview in discord
        emote_e=discord_utils.default_emote('regional_indicator_e'),
        emote_n=discord_utils.default_emote('regional_indicator_n')
    )
    discord_interactions.respond_to_discord_interaction(
        interaction_token=info.interaction_token,
        message=message
    )
