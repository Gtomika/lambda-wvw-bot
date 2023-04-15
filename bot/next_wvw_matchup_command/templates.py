matchup_calculation_in_progress = {
    'hu': 'Matchup lekérdezése és elemzése. Kis türelmet... {emote_loading}'
}

relink_response = {
    'hu': 'A következő reset egyben re-link is lesz {emote_link}. Ilyen esetben semmi nem tudható a következő matchup-ról.'
}

next_matchup_response = {
    'hu': """**Jóslat**: {home_world_name} következő matchup-ja

Figyelem, ez csak akkor lesz így, ha a jelenlegi sorrend a csapatok között nem változik reset-ig {emote_warning}!

A világ jelenlegi szintje: Tier {tier}
{prediction_string}
 
Ezek a szerverek lehetnek a következő matchup-ban:
{predicted_teams_string}

Inkább a jelenlegi matchup érdekel? Használd a */wvw_matchup* parancsot!"""
}

prediction = {
    'hu': {
        1: 'Várhatóan feljebb lépünk, új szint: tier {tier} {emote}',
        0: 'Várhatóan ugyanezen a szinten maradunk: tier {tier} {emote}',
        -1: 'Várhatóan visszaesünk, új szint: tier {tier} {emote}'
    }
}

predicted_team = {
    'hu': "- {emote_color}{emote_house} **{main_world_name}** {linked_world_names}"
}