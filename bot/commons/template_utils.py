# to be used when the interaction has no locale or not supported locale
# it must be in ALL template maps
default_locale = 'hu'

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
    - Figyelem, {developer}, ezt a hibát vizsgáld meg!
    """
}


def format_and_respond_internal_error(discord_interactions, discord_utils, info):
    error_message = get_localized_template(common_template_internal_error, info.locale).format(
        developer = discord_utils.mention_user(discord_utils.developer_id)
    )
    discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)


common_template_command_unauthorized = {
    'hu': 'Ehhez nincs jogosultságod, nekem csak egy commander {emote_commander} parancsolhat!'
}


def format_and_respond_to_command_unauthorized(discord_interactions, discord_utils, info):
    error_message = get_localized_template(common_template_command_unauthorized, info.locale)\
        .format(emote_commander=discord_utils.custom_emote('commander', discord_utils.commander_emote_id))
    discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)


common_template_api_key_required = {
    'hu': """Ahhoz, hogy ezt a parancsot végre tudjam hajtani, szükségem van egy GW2 API kulcsra {emote_key}
      - Ilyet az ArenaNet fiókodnál tudsz létrehozni: {anet_applications_url}
      - Add hozzá **legalább** ezeket az engedélyeket: {permissions}
      - Add meg nekem a '/api_key_add' paranccsal.
      - Az API kulcs megadása semmilyen veszélyt nem jelent a GW2 fiókodra. Itt olvashatsz róla bővebben: {api_key_info_url} 
    """
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
      - Ilyet az ArenaNet fiókodnál tudsz létrehozni: {anet_applications_url}
      - Add hozzá **legalább** ezeket az engedélyeket: {permissions}
      - Az új kulcsot add meg nekem a '/api_key_add' parancssal. 
    """
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
     - Reset után néhány óráig a WvW API megbízhatatlan. Ebben az esetben érdemes várni."""
}


def format_and_respond_gw2_api_error(discord_interactions, info):
    error_message = get_localized_template(common_template_gw2_api_error, info.locale)
    discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)


common_template_home_world_not_set = {
    'hu': 'A guild-nek nincs beállított világa! Először állíts be egyet a "/home_world [világ neve]" parancssal (ehhez kezelői jog szükséges).'
}


def format_and_response_home_world_not_set(discord_interactions, info):
    error_message = get_localized_template(common_template_home_world_not_set, info.locale)
    discord_interactions.respond_to_discord_interaction(info.interaction_token, error_message)
