import template_utils

ACK_TYPE = 1
RESPONSE_TYPE = 4
DEFER_TYPE = 5


class InteractionInfo:
    def __init__(self, event):
        self.user_id = extract_user_id(event)
        self.username = extract_username(event)
        self.locale = extract_locale(event)
        self.interaction_token = extract_interaction_token(event)

# ------- data extraction ------------


def extract_info(event) -> InteractionInfo:
    return InteractionInfo(event)


def extract_locale(event) -> str:
    if 'locale' in event:
        return event['locale']
    else:
        return template_utils.default_locale


def extract_username(event) -> str:
    if is_from_guild(event):
        return event['member']['user']['username']
    else:
        return event['user']['username']


def extract_user_id(event) -> int:
    if is_from_guild(event):
        return event['member']['user']['id']
    else:
        return event['user']['id']


def extract_interaction_token(event) -> str:
    return event['token']


def extract_option(event, option_name: str):
    for option in event['options']:
        if option['name'] == option_name:
            return option
    raise Exception(f'Option with name {option_name} was not found')

# ------- event conditions ------------


def is_from_guild(event) -> bool:
    return 'member' in event

# ------- message formatting ------------


def custom_emote(name: str, emote_id: int) -> str:
    return f'<:{name}:{str(emote_id)}>'


def default_emote(name: str) -> str:
    return f':{name}:'


def animated_emote(name: str, emote_id: int) -> str:
    return f'<a:{name}:{str(emote_id)}>'


def mention_user(user_id: int) -> str:
    return f'<@{str(user_id)}>'
