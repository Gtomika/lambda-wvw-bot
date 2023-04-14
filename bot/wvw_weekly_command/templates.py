achievements_response = {
    'hu': """Íme a heti WvW-s teljesítmények {emote_notes}
 
{achievement_details}

{total_rewards}

{summary}"""
}

summary = {
    'hu': 'A GW2 API nem tartalmazza a heti WvW-s teljesítményeket, ezért nem tudom ezekkel hogy állsz. A napi teljesítményeket a */wvw_daily* utasítással kérdezheted le.'
}

total_rewards = {
    'hu': 'Összesített jutalom: 8 {emote_gold} és 2 {emote_potion}. Hat teljesítmény szükséges hozzá és hétfőn reggel 9-kor van a reset.'
}

weekly_detail = {
    'hu': '- **{name}**: {amount} {unit} ({potion_amount} {emote_potion})'
}

# Hardcoded values, because they are not in the API
weekly_achievements = [
    {
        'name': 'Camp Capturer',
        'amount': 15,
        'unit': {
            'hu': 'camp elfoglalása'
        },
        'potion_reward': 2
    },
    {
        'name': 'Dolyak Denier',
        'amount': 15,
        'unit': {
            'hu': 'dolyak lemészárlása'
        },
        'potion_reward': 2
    },
    {
        'name': 'Invader Incinerator',
        'amount': 50,
        'unit': {
            'hu': 'ellenfél elpusztítása'
        },
        'potion_reward': 2
    },
    {
        'name': 'Keep Crusher ',
        'amount': 3,
        'unit': {
            'hu': 'keep elfoglalása'
        },
        'potion_reward': 2
    },
    {
        'name': 'Keep Keeper',
        'amount': 3,
        'unit': {
            'hu': 'keep védelme'
        },
        'potion_reward': 2
    },
    {
        'name': 'Ruin Runner',
        'amount': 5,
        'unit': {
            'hu': 'ruin elfoglalása (shrine nem számít bele)'
        },
        'potion_reward': 2
    },
    {
        'name': 'Stonemist Castle Conquerer',
        'amount': 1,
        'unit': {
            'hu': 'SM elfoglalása'
        },
        'potion_reward': 2
    },
    {
        'name': 'Tower Guardian',
        'amount': 8,
        'unit': {
            'hu': 'tower védelme'
        },
        'potion_reward': 2
    },
    {
        'name': 'Tower Taker',
        'amount': 8,
        'unit': {
            'hu': 'tower elfoglalása'
        },
        'potion_reward': 2
    }
]