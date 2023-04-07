ACK_TYPE = 1
RESPONSE_TYPE = 4
DEFER_TYPE = 5

loading_emote_id = 971306366687928371
gem_emote_id = 970640961468248144
commander_emote_id = 970638912458469426

admin_permission = 0x0000000000000008


class OptionNotFoundException(Exception):
    pass


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
    return event['locale']


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
    """
    Get one option from the interaction event. Throws:
     - OptionNotFoundException
    """
    for option in event['data']['options']:
        if option['name'] == option_name:
            return option
    raise OptionNotFoundException


def extract_member_roles(event):
    """
    Only call this if event is from guild!
    """
    return event['member']['roles']


# ------- event conditions ------------


def is_from_guild(event) -> bool:
    return 'member' in event


def is_admin(event) -> bool:
    if is_from_guild(event):
        permissions = event['member']['permissions']
        return permissions & admin_permission == admin_permission
    else:
        return False

# ------- message formatting ------------


def custom_emote(name: str, emote_id: int) -> str:
    return f'<:{name}:{str(emote_id)}>'


def default_emote(name: str) -> str:
    return f':{name}:'


def animated_emote(name: str, emote_id: int) -> str:
    return f'<a:{name}:{str(emote_id)}>'


def mention_user(user_id: int) -> str:
    return f'<@{str(user_id)}>'
