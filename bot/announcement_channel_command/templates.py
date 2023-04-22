channel_not_provided = {
    'hu': 'Nem adtál meg csatornát, így nem tudom végrehajtani a utasítást!',
    'en': "You haven't provided the channel, so I'm not able to execute the command!"
}

webhook_test = {
    'hu': 'Próba üzenet: ha ezt látod, a hirdető csatorna beállítása sikerült {emote_success}',
    'en': 'Test message: if you see this, the advertiser channel has been set up {emote_success}'
}

channel_added = {
    'hu': """A hirdetéseimet mostantól a {channel} csatornán is közzéteszem {emote_speaker}.

Figyelem: ellenőrizd, hogy a megadott csatornára elküldtem-e a teszt üzenetet! Ha nem látod, akkor a megadott webhook helytelen vagy másik csatornára szól. Ilyen esetben:
- Hozd létre a szerver beállítások (integrációk) menüben a helyes webhook-ot, és azzal próbáld újra.""",

    'en': """I'll now post my reminders to the {channel} channel as well {emote_speaker}.

Attention: Check if I've sent the test message to the specified channel! If you don't see it, then the specified webhook is incorrect or refers to another channel. In this case:
- Create the correct webhook in the server settings (integrations) menu and try again with that."""
}

channel_deleted = {
    'hu': 'A hirdetéseimet mostantól nem teszem közzé a {channel} csatornán {emote_mute}',
    'en': "I won't post my reminders on the {channel} channel anymore {emote_mute}"
}

goodbye_message = {
    'hu': 'Mostantól nem hirdetek ezen a csatornán {emote_wave}',
    'en': "I won't be posting ads on this channel anymore {emote_wave}"
}

channels_listed = {
    'hu': 'Ezeken a csatornákon hirdetek: {channels} {emote_speaker}',
    'en': 'I advertise on these channels: {channels} {emote_speaker}'
}

no_channels = {
    'hu': 'Jelenleg egyetlen csatornán sem hirdetek {emote_mute}',
    'en': "I'm not advertising on any channels right now {emote_mute}"
}

too_much = {
    'hu': 'Nem adhatsz hozzá több csatornát, a maximum **{max}**.',
    'en': "You can't add more channels, the maximum is **{max}**."
}
