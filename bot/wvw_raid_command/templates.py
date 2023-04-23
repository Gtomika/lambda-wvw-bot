time_parsing_failed = {
    'en': "Failed to parse time. Please provide the time in this format: `XX:XX`, for example: `19:00`",
    'hu': 'Nem sikerült beolvasni az időpontot. Ilyen formátumban kell megadni: `XX:XX`, például: `19:00`'
}

raid_added = {
    'en': """I've added this event:
{raid_description}
You can check all events using the `/wvw_raid list` command.""",
    'hu': """Elementettem ezt az eseményt:
{raid_description}
A `/wvw_raid list` utasítással kérheted le az összes eseményt."""
}

raid_deleted = {
    'en': "I've deleted the `{event_name}` event.",
    'hu': "A(z) `{event_name}` eseményt töröltem"
}

raid_not_found = {
    'en': "I couldn't find an event named `{event_name}`, so I didn't delete anything. You can check the events using the `/wvw_raid list` command.",
    'hu': 'Nem találtam `{event_name}` nevű eseményt, ezért nem töröltem semmit. Az eseményeket megnézheted a `/wvw_raid list` utasítással.'
}

raids_listed = {
    'en': """Here are the WvW events that I know of:

{raid_descriptions}""",
    'hu': """Ezekről a WvW eseményekről tudok:

{raid_descriptions}"""
}

raids_not_found = {
    'en': "There are no registered WvW events. You can create one using the `/wvw_raid add` command.",
    'hu': "Nincs egyetlen bejegyzett WvW esemény sem. A `/wvw_raid add` utasítással hozhatsz létre egyet."
}

raid_description = {
    'en': '- **{event_name}**: {day} {time}, Duration: {hours} hours. Next occurrence: `{next_occurrence}` (reminder: {reminder_state})',
    'hu': '- **{event_name}**: {day} {time},  Hossz: {hours} óra. Következő alkalom: `{next_occurrence}` (értesítés: {reminder_state})'
}

too_much = {
    'en': "You can't add more events. The maximum is **{max}**.",
    'hu': 'Nem adhatsz hozzá több eseményt, maximum **{max}** lehet.'
}

name_taken = {
    'en': "There is already an event named `{name}`, please choose a different name.",
    'hu': 'Már van egy `{name}` nevű esemény, kérlek válassz egy másik nevet.'
}

reminder_states = {
    'hu': {
        False: 'nincs',
        True: 'aktív'
    },
    'en': {
        False: 'disabled',
        True: 'active'
    }
}
