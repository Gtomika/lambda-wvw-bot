import requests
import os

discord_api_base_url = 'https://discord.com/api/v10'

# path variables: application ID, interaction token
edit_original_response_url = discord_api_base_url + '/webhooks/{application_id}/{interaction_token}/messages/@original'

application_id = os.getenv('APPLICATION_ID')
bot_token = os.getenv('BOT_TOKEN')


# Sends response to Discord interaction that is in 'deferred' (5) state.
# this is going to use Discord API to make the update.
def respond_to_discord_interaction(interaction_token: str, message: str) -> bool:
    url = edit_original_response_url.format(application_id=application_id, interaction_token=interaction_token)
    response = requests.patch(url, json={
        'content': message
    }, headers={
        'Authorization': f'Bot {bot_token}',
        'Content-Type': 'application/json'
    })

    if response.status_code < 400:
        return True
    else:
        print(f'Error while making edit to original interaction message, status: {response.status_code},'
              f' data: {response.content}')
        return False
