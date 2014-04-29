import datetime
import pytz


def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    delta = dt - epoch
    return delta.total_seconds()


def unix_time_millis(dt):
    return unix_time(dt) * 1000.0