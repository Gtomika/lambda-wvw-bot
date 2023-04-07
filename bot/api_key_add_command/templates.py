success_response_template = {
    'hu': 'Elmentettem az API kulcsot {emote_key}! Eszerint te **{gw2_account_name}** vagy.'
}

unauthorized_response_template = {
    'hu': '''Nem sikerült hitelesíteni ezzel a kulccsal {emote_no_entry}!
    Ellenőrizd, hogy jó kulcsot adtál-e meg, és megvannak rajta ezek az engedélyek: {permissions}'''
}

api_error_response_template = {
    'hu': 'Nem sikerült elérni a GW2 API-t {emote_no_entry}. Ez nem a te hibád, próbáld újra kicsit később.'
}

public_key_response_template = {
    'hu': '''{warning_emote} Nyilvános üzenetben adtad meg az API kulcsodat! {warning_emote} Ezt így nem fogadom el és
    javaslom, hogy készíts egy új kulcsot {emote_key} ehelyett, amit **privát** üzenetben küldj el nekem.'''
}

invalid_key_response_template = {
    'hu': '''Ez nem egy érvényes API kulcs {emote_key}!
    - A kulcsok mindig {api_key_length} karakter hosszúak.
    - A kulcsok egy speciális formátumban vannak megadva.  
    Javaslom, hogy másold ki onnan ahol létrehoztad, így biztos nem rontod el.'''
}
