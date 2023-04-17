

def log_command(info, command_name: str, subcommand_name=None, detail=None):
    if subcommand_name is None:
        subcommand_name = 'none'

    if detail is None:
        detail = 'none'

    if hasattr(info, 'guild_id'):
        source = f'Guild (ID {info.guild_id})'
    else:
        source = 'Private message'

    print(f'Command invocation: "{command_name}". Subcommand: "{subcommand_name}". User: {info.username} (ID {info.user_id}). '
          f'Source: {source}. Detail: {detail}.')
