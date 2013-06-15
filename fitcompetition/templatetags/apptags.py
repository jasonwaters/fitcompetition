from datetime import datetime
from math import floor
import math
from django.template.defaultfilters import register
import pytz
from django.conf import settings


MILLIS_PER_SECOND = 1000
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = SECONDS_PER_MINUTE * MINUTES_PER_HOUR
SECONDS_PER_DAY = SECONDS_PER_MINUTE * MINUTES_PER_HOUR * HOURS_PER_DAY


@register.filter
def toMiles(km):
    if not isinstance(km, float):
        return ""
    return km * 0.62137

@register.filter
def twoDecimals(value):
    return math.ceil(value * 100) / 100

@register.filter
def duration(secs):
    # return str(datetime.timedelta(seconds=secs))
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


@register.filter
def deltaDate(targetDate, kind):
    now = datetime.now(tz=pytz.timezone(getattr(settings, "TIME_ZONE", '')))
    diff = targetDate - now

    negative = diff.total_seconds() < 0

    days = diff.days
    diff = diff.seconds

    hours = floor(diff / SECONDS_PER_HOUR)
    diff %= SECONDS_PER_HOUR

    mins = floor(diff / SECONDS_PER_MINUTE)
    diff %= SECONDS_PER_MINUTE

    secs = floor(diff)

    value = 0

    if kind == "days":
        value = days
    elif kind == "hours":
        value = hours
    elif kind == "mins":
        value = mins
    elif kind == "secs":
        value = secs

    if negative:
        value = 0

    return "{0:02.0f}".format(value)


@register.filter
def fullDate(d):
    return d.isoformat()
