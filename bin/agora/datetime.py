import datetime as dt
import decorator as d

UTC = dt.timezone.utc

def utc_normalize(datetime):
    """
    Takes a datetime and normalizes it to UTC.
    """
    return datetime.astimezone(UTC)

def naive_normalize(datetime):
    """
    Takes a datetime, converts it to UTC, and drops the tzinfo.
    """
    return utc_normalize(datetime).replace(tzinfo=None)

def _normalized(normalizer):
    @d.decorator
    def normalize(f, *args, **kwargs):
        r = f(*args, **kwargs)
        return normalizer(r)
    return normalize

# Decorators
utc = _normalized(utc_normalize)
naive = _normalized(naive_normalize)
