from datetime import timedelta, datetime
from dateutil import parser
from fitcompetition.settings import TIME_ZONE
from fitcompetition.util.ListUtil import attr
import pytz
import requests
from requests_oauthlib import OAuth1
from django.conf import settings


class Integration(object):
    RUNKEEPER = "Runkeeper"
    MAPMYFITNESS = "MapmyFitness"


class ExternalIntegrationException(Exception):
    def __init__(self, message, status_code=None, **kwargs):
        super(ExternalIntegrationException, self).__init__(message, **kwargs)
        self.status_code = status_code

    @property
    def forbidden(self):
        return self.status_code == 403


def getExternalIntegrationService(user):
    if user.integrationName == Integration.RUNKEEPER and user.runkeeperToken is not None and len(user.runkeeperToken) > 0:
        return RunkeeperService(user)
    elif user.integrationName == Integration.MAPMYFITNESS and user.mapmyfitnessToken is not None and len(user.mapmyfitnessToken) > 0:
        return MapMyFitnessService(user)


class Profile(object):
    def __init__(self, user, service):
        self._user = user

        if service == Integration.RUNKEEPER:
            self.medium_picture = user.get('medium_picture')
            self.normal_picture = user.get('normal_picture')
            self.gender = user.get('gender')
            self.profile_url = user.get('profile')
        elif service == Integration.MAPMYFITNESS:
            self.medium_picture = user.get('photos').get('small')[0]['href']
            self.normal_picture = user.get('photos').get('medium')[0]['href']
            self.gender = user.get('gender')
            self.profile_url = "%s/profile/%s/" % (MapMyFitnessService.BASE_URL, str(user.get('id')))

        super(Profile, self).__init__()

    def get(self, name):
        return attr(self, name)


class Activity(object):
    RUNNING = "Running"
    CYCLING = "Cycling"
    MOUNTAIN_BIKING = "Mountain Biking"
    WALKING = "Walking"
    HIKING = "Hiking"
    DOWNHILL_SKIING = "Downhill Skiing"
    SNOWBOARDING = "Snowboarding"
    SKATING = "Skating"
    SWIMMING = "Swimming"
    ROWING = "Rowing"
    ELLIPTICAL = "Elliptical"
    OTHER = "Other"

    def __init__(self, activity, service):
        if service == Integration.RUNKEEPER:
            self.uri = activity.get('uri')
            self.type = activity.get('type')
            self.duration = activity.get('duration')
            self.date = parser.parse(activity.get('start_time')).replace(tzinfo=pytz.timezone(TIME_ZONE))
            self.calories = activity.get('total_calories')
            self.distance = activity.get('total_distance')
            self.hasEvidence = activity.get('has_path')
        elif service == Integration.MAPMYFITNESS:
            #this is a dictionary to match the various mmf workout ids to useful ones
            types = {
                16: self.RUNNING,
                25: self.RUNNING,
                111: self.RUNNING,
                124: self.RUNNING,
                136: self.RUNNING,
                173: self.RUNNING,
                188: self.RUNNING,
                266: self.RUNNING,
                668: self.RUNNING,
                672: self.RUNNING,
                712: self.RUNNING,
                855: self.RUNNING,
                9: self.WALKING,
                117: self.WALKING,
                126: self.WALKING,
                152: self.WALKING,
                204: self.WALKING,
                321: self.WALKING,
                666: self.WALKING,
                670: self.WALKING,
                822: self.WALKING,
                36: self.CYCLING,
                44: self.CYCLING,
                47: self.CYCLING,
                53: self.CYCLING,
                11: self.CYCLING,
                19: self.CYCLING,
                38: self.CYCLING,
                50: self.CYCLING,
                81: self.CYCLING,
                139: self.CYCLING,
                548: self.CYCLING,
                41: self.MOUNTAIN_BIKING,
                22: self.HIKING,
                24: self.HIKING,
                211: self.ELLIPTICAL,
                250: self.ELLIPTICAL,
                74: self.DOWNHILL_SKIING,
                101: self.SKATING,
                107: self.SNOWBOARDING,
                86: self.SKATING,
                169: self.SKATING,
                502: self.SKATING,
                15: self.SWIMMING,
                20: self.SWIMMING,
                75: self.SWIMMING,
                193: self.SWIMMING,
                57: self.ROWING,
                99: self.ROWING,
                128: self.ROWING,
                261: self.ROWING,
            }

            links = activity.get('_links')
            aggregates = activity.get('aggregates')
            activity_type_id = int(links.get('activity_type')[0].get('id'))

            self.type = types.get(activity_type_id, self.OTHER)
            self.uri = links.get('self')[0].get('href')
            self.duration = aggregates.get('elapsed_time_total')

            #activities are stored in utc time but based on the user's local time. We do some date manipulation here to comply with how
            #runkeeper stores their dates, for better or worse.

            activityTimezone = pytz.timezone(activity.get('start_locale_timezone'))
            self.date = activityTimezone.normalize(parser.parse(activity.get('start_datetime')).astimezone(pytz.utc))
            self.date = datetime(self.date.year, self.date.month, self.date.day, self.date.hour, self.date.minute, self.date.second, tzinfo=pytz.utc)

            self.calories = aggregates.get('metabolic_engergy_total', 0) / float(4180)
            self.distance = aggregates.get('distance_total')
            self.hasEvidence = activity.get('has_time_series')

        super(Activity, self).__init__()

    def get(self, name):
        return attr(self, name)


class RunkeeperService(object):
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

    def __init__(self, user):
        self.user = user
        super(RunkeeperService, self).__init__()

    def getFitnessActivities(self, noEarlierThan=None, noLaterThan=None, modifiedSince=None):
        params = {
            'access_token': self.user.runkeeperToken,
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

        url = "%s%s" % (self.RUNKEEPER_API_URL, self.FITNESS_ACTIVITIES)
        r = requests.get(url, params=params, headers=headers)

        if r.status_code == 304:
            # status = 304 ~ not modified
            return []
        elif r.status_code != 200:
            raise ExternalIntegrationException("Status Code: %s" % r.status_code, status_code=r.status_code)

        json = r.json()
        return json.get('items', [])

    def getChangeLog(self, modifiedNoEarlierThan=None, modifiedNoLaterThan=None):
        params = {
            'access_token': self.user.runkeeperToken,
        }

        headers = {}

        if modifiedNoEarlierThan is not None:
            params['modifiedNoEarlierThan'] = modifiedNoEarlierThan.strftime('%Y-%m-%dT%H:%M:%S')

        if modifiedNoLaterThan is not None:
            params['modifiedNoLaterThan'] = modifiedNoLaterThan.strftime('%Y-%m-%dT%H:%M:%S')

        url = "%s%s" % (self.RUNKEEPER_API_URL, self.CHANGE_LOG)
        r = requests.get(url, params=params, headers=headers)

        if r.status_code == 304:
            # status = 304 ~ not modified
            return {}
        elif r.status_code != 200:
            raise ExternalIntegrationException("Status Code: %s" % r.status_code, status_code=r.status_code)

        return r.json()

    def getUserProfile(self):
        params = {
            'access_token': self.user.runkeeperToken,
        }

        url = "%s%s" % (self.RUNKEEPER_API_URL, self.PROFILE)
        r = requests.get(url, params=params)

        if r.status_code != 200:
            raise ExternalIntegrationException("Status Code: %s" % r.status_code, status_code=r.status_code)

        return Profile(r.json(), service=Integration.RUNKEEPER)


class MapMyFitnessService:
    API_URL = "https://api.mapmyapi.com"
    BASE_URL = 'http://mapmyfitness.com'

    def __init__(self, user):
        self.user = user
        self.oauth = OAuth1(getattr(settings, 'SOCIAL_AUTH_MAPMYFITNESS_KEY'),
                            getattr(settings, 'SOCIAL_AUTH_MAPMYFITNESS_SECRET'),
                            unicode(user.mapmyfitnessToken),
                            unicode(user.mapmyfitnessTokenSecret),
                            signature_type='AUTH_HEADER')

    def getOutput(self, json):
        return json.get('result').get('output')

    def getFitnessActivities(self, noEarlierThan=None, noLaterThan=None, modifiedSince=None):
        params = {
            'limit': 1000,
            'user': self.user.username.split('_')[-1],
        }

        if noEarlierThan is not None:
            params['started_after'] = noEarlierThan

        if noLaterThan is not None:
            params['started_before'] = noLaterThan

        if modifiedSince is not None:
            params['updated_after'] = modifiedSince

        r = requests.get('%s/v7.0/workout/' % self.API_URL, auth=self.oauth, params=params)

        if r.status_code != 200:
            raise ExternalIntegrationException("Status Code: %s" % r.status_code, status_code=r.status_code)

        result = r.json()
        return result.get('_embedded').get('workouts')

    def getUserProfile(self):
        r = requests.get('%s/v7.0/user/self/' % self.API_URL, auth=self.oauth)

        if r.status_code != 200:
            raise ExternalIntegrationException("Status Code: %s" % r.status_code, status_code=r.status_code)

        profile = r.json()

        r = requests.get('%s/v7.0/user_profile_photo/%s/' % (self.API_URL, profile.get('id')), auth=self.oauth)

        if r.status_code != 200:
            raise ExternalIntegrationException("Status Code: %s" % r.status_code, status_code=r.status_code)

        profile['photos'] = r.json()['_links']

        return Profile(profile, service=Integration.MAPMYFITNESS)

    def getActivityTypes(self, url='/v7.0/activity_type/'):
        r = requests.get('%s%s' % (self.API_URL, url), auth=self.oauth, params={
            'limit': 40
        })

        if r.status_code != 200:
            raise ExternalIntegrationException("Status Code: %s" % r.status_code, status_code=r.status_code)

        result = r.json()
        activity_types = result.get('_embedded').get('activity_types')

        for type in activity_types:
            print "%s: '%s'" % (type.get('_links').get('self')[0].get('id'), type.get('name'))

        if result.get('_links').get('next'):
            self.getActivityTypes(result.get('_links').get('next')[0].get('href'))

        return activity_types
