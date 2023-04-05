# to be used when the interaction has no locale or not supported locale
# it must be in ALL template maps
default_locale = 'hu'


def get_localized_template(template_map, locale: str) -> str:
    if locale in template_map:
        return template_map[locale]
    else:
        return template_map[default_locale]


common_template_internal_error = {
    'hu': 'Ismeretlen hiba történt! Kérlek próbáld újra, és ha ez továbbra is fent áll, jelezd a készítőmnek!'
}
