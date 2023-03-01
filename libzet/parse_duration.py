from superdate import parse_date


def parse_duration(duration):
    """ Return a timedelta from a duration str.

    Can handle humanized durations. Like "40min" or "1 hour". Handles
    down to minute precision.

    Args:
        duration: Duration to turn into timedelta.

    Returns:
        timedelta object.
    """
    if type(duration) is timedelta:
        return duration

    later = parse_date(duration)
    now = datetime.now()
    now = datetime(now.year, now.month, now.day, now.hour, now.minute)

    return later - now
