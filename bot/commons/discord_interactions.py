import requests
import os

discord_api_base_url = 'https://discord.com/api/v10'
discord_interaction_timeout = 5

# path variables: application ID, interaction token
edit_original_response_url = discord_api_base_url + '/webhooks/{application_id}/{interaction_token}/messages/@original'

application_id = os.getenv('APPLICATION_ID')
bot_token = os.getenv('BOT_TOKEN')


class WebhookPersonality:
    """
    Represents how the bot appears in webhook messages.
    """

    def __init__(self, bot_name: str, bot_icon_url: str):
        self.bot_name = bot_name
        self.bot_icon_url = bot_icon_url


# Sends response to Discord interaction that is in 'deferred' (5) state.
# this is going to use Discord API to make the update.
def respond_to_discord_interaction(interaction_token: str, message: str) -> bool:
    """
    Respond to a discord interaction, identified by the interaction token.
    """
    url = edit_original_response_url.format(application_id=application_id, interaction_token=interaction_token)
    response = requests.patch(url, json={
        'content': message
    }, headers={
        'Authorization': f'Bot {bot_token}',
        'Content-Type': 'application/json'
    }, timeout=discord_interaction_timeout)

    if response.status_code < 400:
        return True
    else:
        print(f'Error while making edit to original interaction message, status: {response.status_code},'
              f' data: {response.content}')
        return False


def create_webhook_message(webhook_url: str, message: str, personality: WebhookPersonality):
    """
    Create a new message on Discord using the given webhook.
    """
    try:
        response = requests.post(url=f'{webhook_url}?wait=true', json={
            'content': message,
            'username': personality.bot_name,
            'avatar_url': personality.bot_icon_url
        }, headers={
            'Content-Type': 'application/json'
        }, timeout=discord_interaction_timeout)

        if response.status_code >= 400:
            print(f"""Error response from Discord API while making webhook request
                - Status {response.status_code}
                - Response: {response.text}""")
    except requests.exceptions.RequestException as e:
        # because the webhook URL is not validated, anything must be expected from the user...
        # in case of invalid URL requests lib will throw this exception: don't want it to propagate
        print(f'Failed to send webhook to Discord. Webhook URL: {webhook_url}. Exception: {str(e)}')
