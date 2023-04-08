import requests

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

def get_wvw_ranks():
    return gw2_api_request(api_key=None, url='/wvw/ranks?ids=all')


def gw2_api_request(api_key, url: str):
    headers = {
            'Authorization': f'Bearer {api_key}'
    } if api_key is not None else None

    response = requests.get(
        url=f'{gw2_api_base_url}{url}',
        headers=headers,
        timeout=gw2_api_timeout
    )
    code = response.status_code
    if code == 401 or code == 403:
        raise ApiKeyUnauthorizedException(f'Unauthorized to make response to GW2 API - code: {response.status_code}, content: {response.content}')
    if 400 <= code < 500:
        raise BadRequestException(f'Bad request made to GW2 API - code: {response.status_code}, content: {response.content}')
    if response.status_code >= 500:
        raise ApiException(f'Internal error from GW2 API - code: {response.status_code}, content: {response.content}')
    return response.json()
