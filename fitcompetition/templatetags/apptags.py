from datetime import datetime
from math import floor
import math
from django.template.defaultfilters import register
from fitcompetition.settings import TIME_ZONE, STATIC_URL
import pytz
from django.conf import settings


MILLIS_PER_SECOND = 1000
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = SECONDS_PER_MINUTE * MINUTES_PER_HOUR
SECONDS_PER_DAY = SECONDS_PER_MINUTE * MINUTES_PER_HOUR * HOURS_PER_DAY


@register.filter
def achievedGoal(meters, goal_miles):
    if not meters:
        return False
    return toMiles(meters) > float(goal_miles)


@register.filter
def overAchiever(meters, goal_miles):
    if not meters:
        return False
    return toMiles(meters) > float(goal_miles) * 1.5


@register.filter
def doubledGoal(meters, goal_miles):
    if not meters:
        return False
    return toMiles(meters) > goal_miles * 2


@register.filter
def isToday(date):
    if not date:
        return False

    diff = date - datetime.now(tz=pytz.timezone(TIME_ZONE))
    return diff.days == 0


@register.filter
def avatar(url):
    if url:
        return url

    return STATIC_URL + 'img/blank-avatar.png'


@register.filter
def toMiles(meters):
    if not isinstance(meters, float):
        return ""
    return meters * 0.00062137


@register.filter
def toLBS(kg):
    if not isinstance(kg, float):
        return ""
    return kg * 2.2046


@register.filter
def twoDecimals(value):
    if not isinstance(value, float):
        return ""
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


@register.filter
def fromSettings(key):
    try:
        setting = getattr(settings, key)
    except AttributeError:
        setting = None

    return setting


@register.filter
def commaSeparated(list, word="or"):
    list = [str(item) for item in list]
    if len(list) == 0:
        return " "
    elif len(list) == 1:
        return list[0]

    all_but_last = ", ".join(list[:-1])
    return "%s %s %s" % (all_but_last, word, list[-1])


@register.inclusion_tag('inclusions/challenges_table.html', takes_context=True)
def challenges_table(context, user, challenges):
    return {'user': user, 'challenges': challenges}
