from bot.commons import template_utils
from bot.commons import discord_utils


astral_acclaim_emote = discord_utils.custom_emote('astral_acclaim', discord_utils.astral_acclaim_emote_id)
complete_emote = discord_utils.default_emote('white_check_mark')


def create_wizards_vault_objectives_message(period: str, gw2_api_wizards_vault_response, locale: str) -> str:
    objective_details = []
    for objective_data in gw2_api_wizards_vault_response['objectives']:
        objective_detail = __create_objective_detail(objective_data, locale)
        objective_details.append(objective_detail)

    period_string = template_utils.get_localized_template(wizard_vault_periods, locale)[period]

    progress_current = gw2_api_wizards_vault_response['meta_progress_current']
    progress_complete = gw2_api_wizards_vault_response['meta_progress_complete']

    return template_utils.get_localized_template(wizards_vault_response, locale).format(
        period=period_string,
        progress_current=str(progress_current),
        progress_complete=str(progress_complete),
        emote_complete=complete_emote if progress_current >= progress_complete else '',
        meta_reward=str(gw2_api_wizards_vault_response['meta_reward_astral']),
        emote_astral_acclaim=astral_acclaim_emote,
        objective_details='\n'.join(objective_details)
    )


def __create_objective_detail(objective_data, locale: str) -> str:
    if is_wvw_objective(objective_data):
        progress_current = objective_data['progress_current']
        progress_complete = objective_data['progress_complete']
        return template_utils.get_localized_template(wizards_vault_wvw_objective, locale).format(
            title=objective_data['title'],
            objective_reward=str(objective_data['acclaim']),
            emote_astral_acclaim=astral_acclaim_emote,
            progress_current=str(progress_current),
            progress_complete=str(progress_complete),
            emote_complete=complete_emote if progress_current >= progress_complete else ''
        )
    else:
        return template_utils.get_localized_template(wizards_vault_non_wvw_objective, locale).format(
            title=objective_data['title'],
            emote_vomiting=discord_utils.default_emote('face_vomiting')
        )


def is_wvw_objective(objective_data) -> bool:
    # Log In is counted as a PvE objective, but it is just as relevant for WvW
    return objective_data['track'] == 'WvW' or objective_data['title'] == 'Log In'


period_daily = 'daily'
period_weekly = 'weekly'

wizard_vault_periods = {
    'en': {
        period_daily: 'daily',
        period_weekly: 'weekly'
    },
    'hu': {
        period_daily: 'napi',
        period_weekly: 'heti'
    }
}

wizards_vault_response = {
    'en': '''Your Wizard's Vault {period} objectives: {progress_current} / {progress_complete} completed {emote_complete}
Meta reward: {meta_reward} {emote_astral_acclaim}

{objective_details}''',
    'hu': '''A {period} Wizard's Vault céljaid: {progress_current} / {progress_complete} teljesítve {emote_complete}
Meta jutalom: {meta_reward} {emote_astral_acclaim}

{objective_details}'''
}

wizards_vault_wvw_objective = {
    'en': '- **{title}** ({objective_reward} {emote_astral_acclaim}): {progress_current} / {progress_complete} completed {emote_complete}',
    'hu': '- **{title}** ({objective_reward} {emote_astral_acclaim}): {progress_current} / {progress_complete} teljesítve {emote_complete}'
}

wizards_vault_non_wvw_objective = {
    'en': '- **{title}**: this is not a WvW related objective {emote_vomiting}',
    'hu': '- **{title}**: ez nem egy WvW-s cél {emote_vomiting}'
}