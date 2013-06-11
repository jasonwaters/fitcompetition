from django.template.defaultfilters import register


@register.filter
def toMiles(km):
    if not isinstance(km, float):
        return ""

    return "%.2f" % (km * 0.62137)


@register.filter
def duration(secs):
    # return str(datetime.timedelta(seconds=secs))
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)