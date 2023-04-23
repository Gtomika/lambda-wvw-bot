achievements_response = {
    'hu': """Íme a heti WvW {emote_wvw} teljesítmények:
 
{achievement_details}

{total_rewards}

{summary}""",
    'en': """Here are the weekly WvW {emote_wvw} achievements:

{achievement_details}

{total_rewards}

{summary}"""
}

summary = {
    'en': 'The GW2 API does not contain weekly WvW data, so I cannot tell you your progress. You can check your daily achievements with the `/wvw_daily` command.',
    'hu': 'A GW2 API nem tartalmazza a heti WvW-s teljesítményeket, ezért nem tudom hogy állsz velük. A napi teljesítményeket a `/wvw_daily` utasítással kérdezheted le.'
}

total_rewards = {
    'en': 'Final rewards: 8 {emote_gold} and 2 {emote_potion}. You need to complete six achievements and the reset is on Monday morning at 9 o\'clock.',
    'hu': 'Végső jutalom: 8 {emote_gold} és 2 {emote_potion}. Hat teljesítmény szükséges hozzá és hétfőn reggel 9-kor van a reset.'
}

weekly_detail = {
    'hu': '- **{name}**: {amount} {unit}, {potion_amount} {emote_potion}'
}

# Hardcoded values, because they are not in the API
weekly_achievements = [
    {
        'name': 'Camp Capturer',
        'amount': 15,
        'unit': {
            'hu': 'camp elfoglalása',
            'en': 'camp captures'
        },
        'potion_reward': 2
    },
    {
        'name': 'Dolyak Denier',
        'amount': 15,
        'unit': {
            'hu': 'dolyak lemészárlása',
            'en': 'dolyak slaughters'
        },
        'potion_reward': 2
    },
    {
        'name': 'Invader Incinerator',
        'amount': 50,
        'unit': {
            'hu': 'ellenfél elpusztítása',
            'en': 'enemies vanquished'
        },
        'potion_reward': 2
    },
    {
        'name': 'Keep Crusher ',
        'amount': 3,
        'unit': {
            'hu': 'keep elfoglalása',
            'en': 'keep captures'
        },
        'potion_reward': 2
    },
    {
        'name': 'Keep Keeper',
        'amount': 3,
        'unit': {
            'hu': 'keep védelme',
            'en': 'keeps protected'
        },
        'potion_reward': 2
    },
    {
        'name': 'Ruin Runner',
        'amount': 5,
        'unit': {
            'hu': 'ruin elfoglalása (shrine nem számít bele)',
            'en': 'ruin captures (shrines do not count)'
        },
        'potion_reward': 2
    },
    {
        'name': 'Stonemist Castle Conquerer',
        'amount': 1,
        'unit': {
            'hu': 'SM elfoglalása',
            'en': 'SM captures'
        },
        'potion_reward': 2
    },
    {
        'name': 'Tower Guardian',
        'amount': 8,
        'unit': {
            'hu': 'tower védelme',
            'en': 'tower defenses'
        },
        'potion_reward': 2
    },
    {
        'name': 'Tower Taker',
        'amount': 8,
        'unit': {
            'hu': 'tower elfoglalása',
            'en': 'tower captures'
        },
        'potion_reward': 2
    }
]