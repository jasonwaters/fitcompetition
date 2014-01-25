from datetime import timedelta
import pytz
import requests

RUNKEEPER_API_URL = 'https://api.runkeeper.com'
USER = '/user'
PROFILE = '/profile'
FITNESS_ACTIVITIES = '/fitnessActivities'
STRENGTH_ACTIVITIES = '/strengthTrainingActivities'
WEIGHT = '/weight'
SETTINGS = '/settings'
DIABETES = '/diabetes'
TEAM = '/team'
SLEEP = '/sleep'
CHANGE_LOG = '/changeLog'
GOALS = '/goals'
NUTRITION = '/nutrition'
GENERAL_MEASUREMENTS = '/generalMeasurements'
BACKGROUND_ACTIVITIES = '/backgroundActivities'
RECORDS = '/records'


class RunkeeperException(Exception):
    pass


def getFitnessActivities(user, noEarlierThan=None, noLaterThan=None, modifiedSince=None):
    params = {
        'access_token': user.runkeeperToken,
        'pageSize': 1000,
    }

    if noEarlierThan is not None:
        params['noEarlierThan'] = noEarlierThan.strftime('%Y-%m-%d')

    if noLaterThan is not None:
        params['noLaterThan'] = noLaterThan.strftime('%Y-%m-%d')

    headers = {}

    if modifiedSince is not None:
        modifiedSince = modifiedSince-timedelta(days=1)
        headers['If-Modified-Since'] = modifiedSince.strftime('%a, %d %b %Y %H:%M:%S GMT')

    url = "%s%s" % (RUNKEEPER_API_URL, FITNESS_ACTIVITIES)
    r = requests.get(url, params=params, headers=headers)

    if r.status_code == 304:
        # status = 304 ~ not modified
        return []
    elif r.status_code != 200:
        raise RunkeeperException("Status Code: %s" % r.status_code)

    json = r.json()
    return json.get('items', [])


def getChangeLog(user, modifiedNoEarlierThan=None, modifiedNoLaterThan=None, modifiedSince=None):
    params = {
        'access_token': user.runkeeperToken,
    }

    headers = {}

    if modifiedSince is not None:
        modifiedSince = modifiedSince-timedelta(days=1)
        headers['If-Modified-Since'] = modifiedSince.replace(tzinfo=pytz.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

    if modifiedNoEarlierThan is not None:
        params['modifiedNoEarlierThan'] = modifiedNoEarlierThan.strftime('%Y-%m-%dT%H:%M:%S')

    if modifiedNoLaterThan is not None:
        params['modifiedNoLaterThan'] = modifiedNoLaterThan.strftime('%Y-%m-%dT%H:%M:%S')

    url = "%s%s" % (RUNKEEPER_API_URL, CHANGE_LOG)
    r = requests.get(url, params=params, headers=headers)

    if r.status_code == 304:
        # status = 304 ~ not modified
        return {}
    elif r.status_code != 200:
        raise RunkeeperException("Status Code: %s" % r.status_code)

    return r.json()


def getUserProfile(user):
    params = {
        'access_token': user.runkeeperToken,
    }

    url = "%s%s" % (RUNKEEPER_API_URL, PROFILE)
    r = requests.get(url, params=params)

    if r.status_code != 200:
        raise RunkeeperException("Status Code: %s" % r.status_code)

    return r.json()
