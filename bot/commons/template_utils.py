# to be used when the interaction has no locale or not supported locale
# it must be in ALL template maps
default_locale = 'en'

anet_accounts_url = 'https://account.arena.net/applications'
api_key_info_url = 'https://wiki.guildwars2.com/wiki/API:API_key'
gw2_api_permissions = "account, inventories, characters, wallet, unlocks, progression"


def get_localized_template(template_map, locale: str):
    if locale in template_map:
        return template_map[locale]
    else:
        return template_map[default_locale]


common_template_internal_error = {
    'hu': """Ismeretlen hiba történt! Kérlek próbáld újra, és ha ez továbbra is fent áll, jelezd a készítőmnek!
- Figyelem, {developer}, ezt a hibát vizsgáld meg.""",
    'en': """An unexpected error happened! Please try again, and if it keeps happening, notify my creator!
- Alarm {developer}, investigate this error."""
}


def format_and_respond_internal_error(discord_interactions, discord_utils, info):
    error_message = get_localized_template(common_template_internal_error, info.locale).format(
        developer=discord_utils.mention_user(discord_utils.developer_id)
    )
    discord_interactions.respond_to_discord_interaction(
        interaction_token=info.interaction_token,
        message=error_message,
        allowed_mention=discord_interactions.allow_user_mentions
    )


common_template_command_unauthorized = {
    'hu': 'Ehhez nincs jogosultságod, nekem csak egy commander {emote_commander} parancsolhat (vagy adminok, vagy kezelő ranggal rendelkezők).',
    'en': 'You are not authorized to perform this command, only a commander {emote_commander} can do that (or server admins, or those with manager roles).'
}


def format_and_respond_to_command_unauthorized(discord_interactions, discord_utils, info):
    error_message = get_localized_template(common_template_command_unauthorized, info.locale)\
        .format(emote_commander=discord_utils.custom_emote('commander', discord_utils.commander_emote_id))
    discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)


common_template_api_key_required = {
    'hu': """Ahhoz, hogy ezt a parancsot végre tudjam hajtani, szükségem van egy GW2 API kulcsra {emote_key}
- Ilyet az ArenaNet fiókodnál tudsz létrehozni: {anet_applications_url}
- Add hozzá **legalább** ezeket az engedélyeket: `{permissions}`
- Add meg nekem a `/api_key set` paranccsal.
- Az API kulcs megadása semmilyen veszélyt nem jelent a GW2 fiókodra. Itt olvashatsz róla bővebben: {api_key_info_url}""",
    'en': """To be able to execute this command, I need a GW2 API key {emote_key}
- You can create one on your ArenaNet account: {anet_applications_url}
- Please grant me **at least** the following permissions: `{permissions}`
- Add the key with the command `/api_key set`.
- Providing your API key doesn't pose any risk to your GW2 account. You can read more about it here: {api_key_info_url}"""
}


def format_and_respond_api_key_required(discord_interactions, discord_utils, info):
    error_message = get_localized_template(common_template_api_key_required, info.locale).format(
        emote_key=discord_utils.default_emote('key'),
        anet_applications_url=discord_utils.escaped_link(anet_accounts_url),
        permissions=gw2_api_permissions,
        api_key_info_url=discord_utils.escaped_link(api_key_info_url)
    )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)


common_template_api_key_unauthorized = {
    'hu': """Az API kulcsodnak {emote_key} nincs meg minden szükséges engedélye, ezért a parancs végrehajtása nem sikerült.
- Kulcsot az ArenaNet fiókodnál tudsz létrehozni: {anet_applications_url}
- Add hozzá **legalább** ezeket az engedélyeket: `{permissions}`
- Az új kulcsot add meg nekem a `/api_key set` parancssal.""",
    'en': """Your API key {emote_key} is hasn't got the required permissions, and I could not perform this action.
- You can create a key at the ANET applications page: {anet_applications_url}
- Add **at least** these permissions to the key: `{permissions}`
- Send me the new key using the `/api_key set` command."""
}


def format_and_respond_api_key_unauthorized(discord_interactions, discord_utils, info):
    error_message = get_localized_template(common_template_api_key_unauthorized, info.locale).format(
        emote_key=discord_utils.default_emote('key'),
        anet_applications_url=discord_utils.escaped_link(anet_accounts_url),
        permissions=gw2_api_permissions
    )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)


common_template_gw2_api_error = {
    'hu': """A GW2 API hibás választ adott, vagy nem válaszolt: sajnos ez előfordul, kérlek próbáld meg újra.
- Reset után néhány óráig a WvW API megbízhatatlan. Ebben az esetben érdemes várni.""",
    'en': """The GW2 API has responded with an error (or has not responded at all). Sometimes this happens, please re-try.
- The WvW API is unreliable for a few hours after reset, it is recommended to wait in this case."""
}


def format_and_respond_gw2_api_error(discord_interactions, info):
    error_message = get_localized_template(common_template_gw2_api_error, info.locale)
    discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)


common_template_home_world_not_set = {
    'hu': 'A guild-nek nincs beállított világa! Először állíts be egyet a `/home_world set` parancssal (ehhez kezelői jog szükséges).',
    'en': 'The guild has no home world set!, Set one first using `/home_world set` (requires managing permissions).'
}


def format_and_respond_home_world_not_set(discord_interactions, info):
    error_message = get_localized_template(common_template_home_world_not_set, info.locale)
    discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)


common_template_invalid_world = {
    'hu': "A `{home_world}` nem egy GW2 világ. Ellenőrizd, hogy nem gépelted-e el. **Figyelem**, a nem angol világoknál a nyelvi tag is a név része, pl: `Dzagonur [DE]`.",
    'en': "`{home_world}` is not a GW2 world. Please check again. **Attention**: for non english worlds, the language tag is part of the worlds name, such as `Dzagonur [DE]`."
}


def format_and_response_invalid_world(discord_interactions, info, world_name: str):
    error_message = get_localized_template(common_template_invalid_world, info.locale).format(
        home_world=world_name
    )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)


populations = {
    'hu': {
        'Low': 'Alacsony',
        'Medium': 'Közepes',
        'High': 'Magas',
        'VeryHigh': 'Nagyon Magas',
        'Full': 'Tele van'
    },
    'en': {
        'Low': 'Low',
        'Medium': 'Medium',
        'High': 'High',
        'VeryHigh': 'Very high',
        'Full': 'Full'
    }
}

transfer_costs = {
    'Low': '500',
    'Medium': '500',
    'High': '1000',
    'VeryHigh': '1800',
    'Full': '-'
}
