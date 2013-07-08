import requests
from urllib import urlencode


RUNKEEPER_API_URL = 'https://api.runkeeper.com'
USER = '/user'
PROFILE = '/profile'
FITNESS_ACTIVITIES = '/fitnessActivities'


def getActivities(user):
    params = {
        'access_token': user.runkeeperToken,
        'pageSize': 100
    }

    url = "%s%s?%s" % (RUNKEEPER_API_URL, FITNESS_ACTIVITIES, urlencode(params))
    r = requests.get(url)
    json = r.json()
    return json.get('items', [])
