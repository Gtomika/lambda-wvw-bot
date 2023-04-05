import requests

gw2_api_base_url = 'https://api.guildwars2.com/v2'
gw2_api_timeout = 10  # sec


# GW2 API 500
class ApiException(Exception):
    pass


# GW2 API 401 or 403
class UnauthorizedException(ApiException):
    pass


class BadRequestException(ApiException):
    pass


def get_account(api_key: str):
    return gw2_api_request(api_key, '/account')


def gw2_api_request(api_key: str, url: str):
    response = requests.get(
        url=f'{gw2_api_base_url}{url}',
        headers={
            'Authorization': f'Bearer {api_key}'
        },
        timeout=gw2_api_timeout
    )
    code = response.status_code
    if code == 401 or code == 403:
        raise UnauthorizedException(f'Unauthorized to make response to GW2 API - code: {response.status_code}, content: {response.content}')
    if 400 <= code < 500:
        raise BadRequestException(f'Bad request made to GW2 API - code: {response.status_code}, content: {response.content}')
    if response.status_code >= 500:
        raise ApiException(f'Internal error from GW2 API - code: {response.status_code}, content: {response.content}')
    return response.json()
