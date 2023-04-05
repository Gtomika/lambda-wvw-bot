import os

import discord_interactions
import discord_utils
import template_utils
import templates


discord_developer_id = int(os.environ['DISCORD_DEVELOPER_ID'])
documentation_url = os.environ['DOCUMENTATION_URL']


def lambda_handler(event, context):
    """
    Handler for the 'help' slash command
    """

    response_template = template_utils.get_localized_template(
        template_map=templates.help_response_template,
        locale=discord_utils.extract_locale(event)
    )
    message = response_template.format(
        developer=discord_utils.mention_user(discord_developer_id),
        emote_docu=discord_utils.default_emote('bookmark_tabs'),
        docu_url=f'<{documentation_url}>',  # <> symbols disable preview in discord
        emote_e=discord_utils.default_emote('regional_indicator_e'),
        emote_n=discord_utils.default_emote('regional_indicator_n')
    )
    discord_interactions.respond_to_discord_interaction(
        interaction_token=discord_utils.extract_interaction_token(event),
        message=message
    )
