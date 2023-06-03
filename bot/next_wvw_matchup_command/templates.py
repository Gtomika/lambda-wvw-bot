matchup_calculation_in_progress = {
    'en': 'Retrieving and analyzing matchup data. Please wait... {emote_loading}',
    'hu': 'Matchup lekérdezése és elemzése. Kis türelmet... {emote_loading}'
}

next_matchup_response = {
    'en': """**Prediction**: {home_world_name}'s next matchup

{matchup_prediction}

Note that this will only be the case if the current order between the teams does not change until reset {emote_warning}!
Prefer to see the current matchup instead? Use the `/wvw_matchup` command!""",

    'hu': """**Jóslat**: {home_world_name} következő matchup-ja

{matchup_prediction}

Figyelem, ez csak akkor lesz így, ha a jelenlegi sorrend a csapatok között nem változik reset-ig {emote_warning}!
Inkább a jelenlegi matchup érdekel? Használd a `/wvw_matchup` parancsot!"""
}

# the detailed templates are in matchup_utils.py, because they are used by multiple commands
