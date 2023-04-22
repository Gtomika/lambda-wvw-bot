matchup_calculation_in_progress = {
    'en': 'Retrieving and analyzing matchup data. Please wait... {emote_loading}',
    'hu': 'Matchup lekérdezése és elemzése. Kis türelmet... {emote_loading}'
}

relink_response = {
    'en': 'The next reset will also be a re-link {emote_link}. In this case, nothing can be known about the next matchup.',
    'hu': 'A következő reset egyben re-link is lesz {emote_link}. Ilyen esetben semmi nem tudható a következő matchup-ról.'
}

next_matchup_response = {
    'en': """**Prediction**: {home_world_name}'s next matchup

Note that this will only be the case if the current order between the teams does not change until reset {emote_warning}!

Current world tier: Tier {tier}
{prediction_string}

These worlds may be in the next matchup:
{predicted_teams_string}

Prefer to see the current matchup instead? Use the `/wvw_matchup` command!""",

    'hu': """**Jóslat**: {home_world_name} következő matchup-ja

Figyelem, ez csak akkor lesz így, ha a jelenlegi sorrend a csapatok között nem változik reset-ig {emote_warning}!

A világ jelenlegi szintje: Tier {tier}
{prediction_string}

Ezek a szerverek lehetnek a következő matchup-ban:
{predicted_teams_string}

Inkább a jelenlegi matchup érdekel? Használd a `/wvw_matchup` parancsot!"""
}

prediction = {
    'hu': {
        1: 'Várhatóan feljebb lép, új szint: tier {tier} {emote}',
        0: 'Várhatóan ugyanezen a szinten marad: tier {tier} {emote}',
        -1: 'Várhatóan visszaesik, új szint: tier {tier} {emote}'
    },
    'en': {
        1: 'Most likely advancing to: tier {tier} {emote}',
        0: 'Most likely staying in the current tier: tier {tier} {emote}',
        -1: 'Most likely dropping to: tier {tier} {emote}'
    }
}

predicted_team = {
    'hu': "- {emote_color}{emote_house} **{main_world_name}** {linked_world_names}",
    'en': "- {emote_color}{emote_house} **{main_world_name}** {linked_world_names}"
}
