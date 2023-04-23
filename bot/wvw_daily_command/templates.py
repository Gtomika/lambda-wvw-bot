today_tomorrow = {
    'hu': {
        False: 'mai',
        True: 'holnapi'
    },
    'en': {
        False: 'today',
        True: 'tomorrow'
    }
}


achievements_response = {
    'hu': """Íme a(z) {day} WvW-s teljesítmények {emote_wvw}
    
    {achievement_details}
    
    {total_rewards}
    
    {summary}""",
    'en': """Here are the WvW achievements for {day} {emote_wvw}
    
    {achievement_details}
    
    {total_rewards}
    
    {summary}"""
}

summary_progress = {
    'hu': 'A GW2 API nem tartalmazza a napi WvW-s teljesítményeket, ezért nem tudom hogy állsz velük. A heti teljesítményeket a `/wvw_weekly` utasítással kérdezheted le.',
    'en': 'The GW2 API does not include daily WvW achievements, so I cannot tell you your progress. You can check your weekly achievements with the `/wvw_weekly` command.'
}

total_rewards = {
    'hu': 'Végső jutalom: 2 {emote_gold}. Három teljesítmény szükséges hozzá és éjjel 2 körül van a reset.',
    'en': 'Final reward: 2 {emote_gold}. Three achievements are required, and the reset occurs around 2 AM.'
}

loading = {
    'hu': "Napi teljesítmények lekérdezése... {emote_loading}",
    'en': "Querying daily achievements... {emote_loading}"
}
daily_detail = {
    'hu': '- **{name}**: {description} {potion_amount} {emote_potion}'
}
