loading = {
    'hu': 'Legendás WvW-s tárgyaid vizsgálata {emote_eyes}... {emote_loading}',
    'en': 'Checking your legendary WvW items {emote_eyes}... {emote_loading}'
}

legendaries_response = {
    'hu': """Ezeket a legendás WvW {emote_wvw} tárgyakat találtam nálad:
{non_armor_legendary_details}
{light_armor_details}
{medium_armor_details}
{heavy_armor_details}""",
    'en': """I found the following legendary WvW {emote_wvw} items on your account:
{non_armor_legendary_details}
{light_armor_details}
{medium_armor_details}
{heavy_armor_details}"""
}

non_armor_detail = {
    'hu': '- **{legendary_name}** {emote_legendary}: {state} {emote_state}',
    'en': '- **{legendary_name}** {emote_legendary}: {state} {emote_state}'
}

armor_detail = {
    'hu': '- **Legendás WvW {armor_weight} páncélzat** {emote_armor}: {amount}/{max} darab',
    'en': '- **Legendary WvW {armor_weight} armor** {emote_armor}: {amount}/{max} pieces'
}

armor_weights = {
    'hu': {
        'light': 'könnyű',
        'medium': 'közepes',
        'heavy': 'nehéz'
    },
    'en': {
        'light': 'light',
        'medium': 'medium',
        'heavy': 'heavy'
    }
}

states = {
    'hu': {
        True: 'megvan',
        False: 'nincs meg'
    },
    'en': {
        True: 'you have it',
        False: 'you don\'t have it'
    }
}
