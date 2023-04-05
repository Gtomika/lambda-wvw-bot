import requests
import os

command_type = os.getenv('COMMAND_TYPE')  # GLOBAL or GUILD
application_id = os.getenv('APPLICATION_ID')
guild_id = os.getenv('GUILD_ID')  # required of 'COMMAND_TYPE' is GUILD
bot_token = os.getenv('DISCORD_BOT_TOKEN')


def register_slash_command(command_json_path: str):
    with open(command_json_path, 'r') as command_file:
        command_data = command_file.read()

    create_command_url = format_register_url(application_id, guild_id)
    print(f'Making create command request to {create_command_url}')

    response = requests.post(create_command_url, data=command_data.encode('utf-8'), headers={
        'Authorization': f'Bot {bot_token}',
        'Content-Type': 'application/json'
    })

    if response.status_code < 400:
        print(f'Registered discord slash command: {command_json_path}')
    else:
        print(f'{response.status_code} Error while registering slash command: {response.content}')


def format_register_url(application_id: str, guild_id: str):
    if command_type == 'GLOBAL':
        return 'https://discord.com/api/v10/applications/{application_id}/commands'\
            .format(application_id=application_id)
    elif command_type == 'GUILD':
        return 'https://discord.com/api/v10/applications/{application_id}/guilds/{guild_id}/commands' \
            .format(application_id=application_id, guild_id=guild_id)
    else:
        print(f"Unknown command type: {command_type}")
        exit(-1)


command_data_folder = os.path.join(os.path.dirname(__file__), 'commands_data')
print(f'Proceeding to register slash commands in {command_data_folder}')

command_data_files = os.listdir(command_data_folder)
for command_data_file in command_data_files:
    register_slash_command(os.path.join(os.path.dirname(__file__), 'commands_data', command_data_file))

print('Registered all slash commands')
if command_type == 'GLOBAL':
    print('Warning: global commands need up to 1 hour after registering/updating to display in Discord')
