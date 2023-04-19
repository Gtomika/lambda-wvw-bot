import requests
from requests.utils import requote_uri

gw2_api_base_url = 'https://api.guildwars2.com/v2'
gw2_api_timeout = 10  # sec

# GW2 API 500
class ApiException(Exception):
    pass


# GW2 API 401 or 403
class ApiKeyUnauthorizedException(ApiException):
    pass


class BadRequestException(ApiException):
    pass


def get_account(api_key: str):
    return gw2_api_request(api_key=api_key, url='/account')


def get_home_worlds():
    return gw2_api_request(api_key=None, url='/worlds?ids=all')


def get_home_world_by_id(world_id: int):
    return gw2_api_request(api_key=None, url=f'/worlds?ids={str(world_id)}')[0]


def get_home_worlds_by_ids(world_ids):
    ids_as_string = ','.join([str(world_id) for world_id in world_ids])
    return gw2_api_request(api_key=None, url=f'/worlds?ids={ids_as_string}')


def get_wvw_ranks():
    return gw2_api_request(api_key=None, url='/wvw/ranks?ids=all')


def get_wvw_matchup_report_of_world(world_id: int):
    return gw2_api_request(api_key=None, url=f'/wvw/matches?world={str(world_id)}')


def get_wvw_matchup_report_by_id(matchup_id: str):
    return gw2_api_request(api_key=None, url=f'/wvw/matches/{matchup_id}')


def get_daily_achievements(tomorrow: bool):
    return gw2_api_request(api_key=None, url='/achievements/daily/tomorrow' if tomorrow else '/achievements/daily')


def get_achievements_by_ids(ids):
    ids_query = ','.join([str(achi_id) for achi_id in ids])
    return gw2_api_request(api_key=None, url=f'/achievements?ids={ids_query}')


def get_achievement_progress_by_ids(api_key: str, ids):
    ids_query = ','.join([str(achi_id) for achi_id in ids])
    return gw2_api_request(api_key=api_key, url=f'/account/achievements?ids={ids_query}')


def get_wallet(api_key: str):
    return gw2_api_request(api_key=api_key, url='/account/wallet')


def get_bank(api_key: str):
    return gw2_api_request(api_key=api_key, url='/account/bank')


def get_material_storage(api_key: str):
    return gw2_api_request(api_key=api_key, url='/account/materials')


def get_character_names(api_key: str):
    return gw2_api_request(api_key=api_key, url='/characters')


def get_character_inventory(api_key: str, character_name: str):
    # required because character name can be strange value...
    quoted_url = requote_uri(f'/characters/{character_name}/inventory')
    return gw2_api_request(api_key=api_key, url=quoted_url)


def get_shared_inventory(api_key: str):
    return gw2_api_request(api_key=api_key, url='/account/inventory')


def get_legendary_armory(api_key: str):
    return gw2_api_request(api_key=api_key, url='/account/legendaryarmory')


def gw2_api_request(api_key, url: str):
    headers = {
            'Authorization': f'Bearer {api_key}'
    } if api_key is not None else None

    try:
        response = requests.get(
            url=f'{gw2_api_base_url}{url}',
            headers=headers,
            timeout=gw2_api_timeout
        )
    except requests.exceptions.ReadTimeout:
        print(f'The request to the GW2 API timed out. Relative URL: {url}')
        raise ApiException

    code = response.status_code
    if code == 401 or code == 403:
        print(f'Unauthorized to make response to GW2 API - code: {response.status_code}, content: {response.content}')
        raise ApiKeyUnauthorizedException
    if 400 <= code < 500:
        print(f'Bad request made to GW2 API - code: {response.status_code}, content: {response.content}')
        raise BadRequestException
    if response.status_code >= 500:
        print(f'Internal error from GW2 API - code: {response.status_code}, content: {response.content}')
        raise ApiException
    return response.json()
