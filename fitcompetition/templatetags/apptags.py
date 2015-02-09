from datetime import datetime
from decimal import Decimal
from math import floor
import math
from django import template
from django.template import Node
from django.template.defaultfilters import register
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from fitcompetition.settings import STATIC_URL, TIME_ZONE
from django.conf import settings
import pytz
import locale
from rest_framework.renderers import JSONRenderer


MILLIS_PER_SECOND = 1000
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = SECONDS_PER_MINUTE * MINUTES_PER_HOUR
SECONDS_PER_DAY = SECONDS_PER_MINUTE * MINUTES_PER_HOUR * HOURS_PER_DAY


@register.filter
def abs(value):
    return math.fabs(value)


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
def tripledGoal(meters, goal_miles):
    if not meters:
        return False
    return toMiles(meters) > goal_miles * 3


@register.filter
def isToday(date):
    if not date:
        return False
    now = timezone.localtime(timezone.now())
    return date.astimezone(pytz.timezone(TIME_ZONE)).date() == now.date()


@register.filter
def avatar(url):
    if url:
        return url

    return STATIC_URL + 'img/blank-avatar.png'


@register.filter(javascriptis_safe=True)
def serialize(obj, serializer):
    mod = __import__('fitcompetition.serializers', fromlist=[serializer])
    klass = getattr(mod, serializer)

    serializedObj = klass(obj)
    return mark_safe(JSONRenderer().render(serializedObj.data))

@register.filter
def toMiles(meters):
    if not isinstance(meters, float):
        return 0
    return meters * 0.00062137


@register.filter
def toMeters(miles):
    return Decimal(miles) / Decimal(0.00062137)


@register.filter
def toLBS(kg):
    if not isinstance(kg, float):
        return 0
    return kg * 2.2046


@register.filter
def twoDecimals(value):
    if not isinstance(value, float):
        return 0
    return math.ceil(value * 100) / 100


@register.filter
def duration(secs):
    if secs is None:
        m, s, h, m = 0, 0, 0, 0
    else:
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)

    return "%02d:%02d:%02d" % (h, m, s)


@register.filter
def daysUntil(targetdate):
    now = datetime.now(tz=pytz.timezone(TIME_ZONE))
    delta = targetdate - now
    return "%s days" % delta.days


@register.filter
def daysSince(targetdate):
    now = datetime.now(tz=pytz.timezone(TIME_ZONE))
    delta = now - targetdate
    return "%s days" % delta.days

@register.filter()
def https(value):
    if value is not None:
        value = value.replace("http://", "https://", 1)
    return value

@register.filter()
def isChallenger(challenge, user):
    if not user.is_authenticated():
        return False

    return user in challenge.players.all()

@register.filter
def deltaDate(targetDate, kind):
    now = datetime.now(tz=pytz.timezone(TIME_ZONE))
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
def hostUrl(request):
    return '%s://%s' % ('https' if request.is_secure() else 'http', request.get_host())


@register.filter
def hashtaggify(value):
    return value.replace(' ', '')


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
def positive(value):
    return math.fabs(value)


@register.filter
def currency(value):
    locale.setlocale(locale.LC_ALL, getattr(settings, 'LOCALE'))
    return locale.currency(value)


@register.filter
def userAchievedChallenge(challenge, user):
    return challenge.getAchievedGoal(user)


@register.filter
def challengeType(challenge):
    if challenge.isTypeIndividual:
        return "Individual Challenge"
    elif challenge.isTypeTeam:
        return 'Team Challenge'


@register.filter
def challengeStyle(challenge):
    if challenge.isStyleAllCanWin:
        return "All Can Win"
    elif challenge.isStyleWinnerTakesAll:
        return 'Winner Takes All'


@register.filter
def commaSeparated(list, word="or"):
    list = [str(item) for item in list]
    if len(list) == 0:
        return " "
    elif len(list) == 1:
        return list[0]

    all_but_last = ", ".join(list[:-1])
    return "%s %s %s" % (all_but_last, word, list[-1])


@register.filter(javascriptis_safe=True)
def activityIcons(activities):
    result = ""
    for activity in activities:
        result += "<span class='activity-icon %s' title='%s'></span>" % (slugify(activity), activity)

    return mark_safe(result)


@register.filter
def times(number):
    if number is None:
        return range(0)

    return range(number)


@register.filter
def pastTense(value):
    return {
        'Running': 'ran',
        'Cycling': 'rode',
        'Mountain Biking': 'rode',
        'Walking': 'walked',
        'Hiking': 'hiked',
        'Downhill Skiing': 'downhill skied',
        'Cross-Country Skiing': 'cross-country skied',
        'Snowboarding': 'snowboarded',
        'Skating': 'skated',
        'Swimming': 'swam',
        'Wheelchair': 'wheeled',
        'Rowing': 'rowed',
        'Elliptical': 'ellipticaled',
        'Other': '',
    }[value]


@register.tag(name='aggregate')
def do_aggregate(parser, token):
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("'aggregate' node requires a variable name.")
    nodelist = parser.parse(('endaggregate',))
    parser.delete_first_token()
    return AggregateNode(nodelist, args)


class AggregateNode(Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        output = self.nodelist.render(context)
        if self.varname in context:
            context[self.varname] += output
            context.dicts[0][self.varname] += output
        else:
            # context[self.varname] = output
            context.dicts[0][self.varname] = output
        return u''


@register.inclusion_tag('inclusions/challenges_table.html', takes_context=False)
def challenges_table(user, challenges, title, iconClass=None, deemphasize=False, hilight=True):
    return {'user': user,
            'challenges': challenges,
            'title': title,
            'iconClass': iconClass,
            'deemphasize': deemphasize,
            'hilight': hilight}


@register.inclusion_tag('inclusions/player_row.html', takes_context=False)
def player_row(user, player, challenge, rank, offset=0):
    return {'user': user,
            'player': player,
            'challenge': challenge,
            'rank': rank + offset}