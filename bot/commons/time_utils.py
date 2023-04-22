import pendulum

__date_time_format = 'YYYY-MM-DD HH:mm'

# if this is changed, also change the command description '/wvw_raid add'
reminder_delay_minutes = 30


def format_date_time(dt: pendulum.DateTime) -> str:
    return dt.format(fmt=__date_time_format)


def validate_time_input(time: str) -> str:
    """
    Expected format like XX:XX, for example 20:00.
    Throws pendulum parse exception
    If input is valid, returns it
    """
    pendulum.parse(time)
    return time


def find_next_occurrence(day: str, time: str) -> pendulum.DateTime:
    """
    Finds when the selected day and selected time will next happen.
    day can be: monday, tuesday, ... , sunday, every_day
    """
    parsed_time = pendulum.parse(time)
    hours = parsed_time.hour
    minutes = parsed_time.minute

    if day == 'every_day':
        # event happens every day. has it already happened today?
        event_today = pendulum.today().at(hour=hours, minute=minutes)
        if event_today.is_past():
            # it has already happened today, move to tomorrow
            return event_today.add(days=1)
        else:
            # it is going to happen today
            return event_today
    else:  # day is a concrete day
        event_day = day_mappings[day]
        today = pendulum.today()
        if today.day_of_week == event_day:
            # the event is today, but has it happened or not yet?
            event_today = pendulum.today().at(hour=hours, minute=minutes)
            if event_today.is_past():
                # it has already happened today, move to occurrence
                return event_today.add(weeks=1)
            else:
                # it is going to happen today
                return event_today
        else:
            # the event is not today
            return today.next(day_of_week=event_day).at(hour=hours, minute=minutes)


day_mappings = {
    'monday': pendulum.MONDAY,
    'tuesday': pendulum.TUESDAY,
    'wednesday': pendulum.WEDNESDAY,
    'thursday': pendulum.THURSDAY,
    'friday': pendulum.FRIDAY,
    'saturday': pendulum.SATURDAY,
    'sunday': pendulum.SUNDAY,
    'every_day': 100  # just has to be bigger than all other
}

day_localizations = {
    'hu': {
        'monday': 'hétfő',
        'tuesday': 'kedd',
        'wednesday': 'szerda',
        'thursday': 'csütörtök',
        'friday': 'péntek',
        'saturday': 'szombat',
        'sunday': 'vasárnap',
        'every_day': 'minden nap'
    },
    'en': {
        'monday': 'monday',
        'tuesday': 'tuesday',
        'wednesday': 'wednesday',
        'thursday': 'thursday',
        'friday': 'friday',
        'saturday': 'saturday',
        'sunday': 'sunday',
        'every_day': 'every day'
    }
}

locale_time_zones = {
    'hu': "Europe/Budapest",
    'en': "Europe/Budapest"  # TODO maybe another TZ is better for 'en'?
}
