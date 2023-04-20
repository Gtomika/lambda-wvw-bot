import traceback

from bot.commons import discord_interactions
from bot.commons import discord_utils
from bot.commons import template_utils
from bot.commons import monitoring
from . import templates

documentation_url = 'https://gtomika.github.io/lambda-wvw-bot'
source_code_url = 'https://github.com/Gtomika/lambda-wvw-bot'


def lambda_handler(event, context):
    """
    Handler for the 'help' slash command
    """
    info = discord_utils.InteractionInfo(event)
    monitoring.log_command(info, 'help')
    try:
        response_template = template_utils.get_localized_template(
            template_map=templates.help_response_template,
            locale=info.locale
        )
        message = response_template.format(
            developer=discord_utils.mention_user(discord_utils.developer_id),
            emote_docu=discord_utils.default_emote('bookmark_tabs'),
            docu_url=discord_utils.escaped_link(documentation_url),
            source_url=discord_utils.escaped_link(source_code_url),
            emote_e=discord_utils.default_emote('regional_indicator_e'),
            emote_n=discord_utils.default_emote('regional_indicator_n')
        )
        discord_interactions.respond_to_discord_interaction(
            interaction_token=info.interaction_token,
            message=message
        )
    except BaseException as e:
        print(f'Error while responding to help command of user {info.username}')
        traceback.print_exc()
        template_utils.format_and_respond_internal_error(discord_interactions, discord_utils, info)
