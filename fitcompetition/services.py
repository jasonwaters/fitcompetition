from datetime import timedelta, datetime
from dateutil import parser
from fitcompetition.settings import TIME_ZONE
from fitcompetition.util.DateUtil import unix_time
from fitcompetition.util.ListUtil import attr
import pytz
import requests
from requests_oauthlib import OAuth1
from django.conf import settings


class Integration(object):
    RUNKEEPER = "Runkeeper"
    MAPMYFITNESS = "MapMyFitness"
    STRAVA = "Strava"

    @staticmethod
    def all():
        return [Integration.RUNKEEPER, Integration.MAPMYFITNESS, Integration.STRAVA]


class ExternalIntegrationException(Exception):
    def __init__(self, message, status_code=None, **kwargs):
        super(ExternalIntegrationException, self).__init__(message, **kwargs)
        self.status_code = status_code

    @property
    def forbidden(self):
        return self.status_code == 403

    @property
    def unauthorized(self):
        return self.status_code == 401


def getExternalIntegrationService(user):
    if user.integrationName == Integration.RUNKEEPER:
        return RunkeeperService(user)
    elif user.integrationName == Integration.MAPMYFITNESS:
        return MapMyFitnessService(user)
    elif user.integrationName == Integration.STRAVA:
        return StravaService(user)


class Profile(object):
    def __init__(self, user, service):
        self._user = user

        if service == Integration.RUNKEEPER:
            fullname = user.get('name', '')

            if fullname:
                try:
                    first_name, last_name = fullname.rsplit(' ', 1)
                except ValueError:
                    if fullname is not None and len(fullname) > 0:
                        first_name = fullname
                    else:
                        first_name = "Unnamed"
                    last_name = ""

            self.firstname = first_name
            self.lastname = last_name
            self.medium_picture = user.get('medium_picture')
            self.normal_picture = user.get('normal_picture')
            self.gender = user.get('gender')
            self.profile_url = user.get('profile')
        elif service == Integration.MAPMYFITNESS:
            self.firstname = user.get('first_name')
            self.lastname = user.get('last_name')
            self.medium_picture = user.get('photos').get('small')[0]['href'] if "static.mapmyfitness.com/d/website/avatars/" not in user.get('photos').get('small')[0]['href'] else None
            self.normal_picture = user.get('photos').get('medium')[0]['href'] if "static.mapmyfitness.com/d/website/avatars/" not in user.get('photos').get('medium')[0]['href'] else None
            self.gender = user.get('gender')
            self.profile_url = "%s/profile/%s/" % (MapMyFitnessService.BASE_URL, str(user.get('id')))
        elif service == Integration.STRAVA:
            self.firstname = user.get('firstname')
            self.lastname = user.get('lastname')
            self.medium_picture = user.get('profile_medium') if "medium.png" not in user.get('profile_medium') else None
            self.normal_picture = user.get('profile') if "large.png" not in user.get('profile') else None
            self.gender = user.get('sex')
            self.profile_url = "http://www.strava.com/athletes/%s" % user.get('id')

        super(Profile, self).__init__()

    @property
    def fullname(self):
        return "%s %s" % (self.firstname, self.lastname)

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

    def __init__(self, activity, service, timezoneString):
        if service == Integration.RUNKEEPER:
            self.uri = activity.get('uri')
            self.type = activity.get('type')
            self.duration = activity.get('duration')

            #runkeeper does not provide timezone data.
            naive = parser.parse(activity.get('start_time'))
            activity_date = naive

            if timezoneString is not None:
                try:
                    # use the user timezone (if set) to localize the date
                    user_tz = pytz.timezone(timezoneString)
                    activity_date = user_tz.localize(naive, is_dst=False)
                except pytz.UnknownTimeZoneError:
                    # inadequate user timezone, leave it naive
                    activity_date = naive

            self.date = activity_date
            self.calories = activity.get('total_calories')
            self.distance = activity.get('total_distance')
            self.hasGPS = activity.get('has_path')
        elif service == Integration.MAPMYFITNESS:
            #this is a dictionary to match the various mmf workout ids to useful ones
            types = {
                16: self.RUNNING,
                246: self.RUNNING,
                102: self.RUNNING,
                243: self.RUNNING,
                855: self.RUNNING,
                283: self.RUNNING,
                218: self.RUNNING,
                124: self.RUNNING,
                227: self.RUNNING,
                197: self.RUNNING,
                136: self.RUNNING,
                831: self.RUNNING,
                829: self.RUNNING,
                188: self.RUNNING,
                172: self.RUNNING,
                187: self.RUNNING,
                118: self.RUNNING,
                712: self.RUNNING,
                91: self.RUNNING,
                103: self.RUNNING,
                282: self.RUNNING,
                173: self.RUNNING,
                115: self.RUNNING,
                108: self.RUNNING,
                266: self.RUNNING,
                25: self.RUNNING,
                250: self.RUNNING,
                756: self.RUNNING,
                268: self.RUNNING,
                208: self.RUNNING,


                9: self.WALKING,
                272: self.WALKING,
                106: self.WALKING,
                253: self.WALKING,
                204: self.WALKING,
                179: self.WALKING,
                145: self.WALKING,
                242: self.WALKING,
                269: self.WALKING,
                264: self.WALKING,
                766: self.WALKING,
                274: self.WALKING,
                117: self.WALKING,
                275: self.WALKING,
                105: self.WALKING,
                126: self.WALKING,
                827: self.WALKING,
                825: self.WALKING,
                152: self.WALKING,
                143: self.WALKING,
                129: self.WALKING,
                133: self.WALKING,
                146: self.WALKING,
                262: self.WALKING,


                11: self.CYCLING,
                56: self.CYCLING,
                648: self.CYCLING,
                52: self.CYCLING,
                465: self.CYCLING,
                466: self.CYCLING,
                60: self.CYCLING,
                549: self.CYCLING,
                550: self.CYCLING,
                710: self.CYCLING,
                33: self.CYCLING,
                618: self.CYCLING,
                619: self.CYCLING,
                64: self.CYCLING,
                653: self.CYCLING,
                652: self.CYCLING,
                50: self.CYCLING,
                615: self.CYCLING,
                36: self.CYCLING,
                637: self.CYCLING,
                638: self.CYCLING,
                633: self.CYCLING,
                636: self.CYCLING,
                634: self.CYCLING,
                632: self.CYCLING,
                640: self.CYCLING,
                635: self.CYCLING,
                629: self.CYCLING,
                631: self.CYCLING,
                639: self.CYCLING,
                630: self.CYCLING,
                641: self.CYCLING,
                38: self.CYCLING,
                445: self.CYCLING,
                44: self.CYCLING,
                523: self.CYCLING,
                702: self.CYCLING,
                47: self.CYCLING,
                545: self.CYCLING,
                544: self.CYCLING,
                139: self.CYCLING,
                92: self.CYCLING,
                81: self.CYCLING,


                41: self.MOUNTAIN_BIKING,
                457: self.MOUNTAIN_BIKING,
                455: self.MOUNTAIN_BIKING,
                454: self.MOUNTAIN_BIKING,
                458: self.MOUNTAIN_BIKING,
                452: self.MOUNTAIN_BIKING,
                462: self.MOUNTAIN_BIKING,
                456: self.MOUNTAIN_BIKING,
                453: self.MOUNTAIN_BIKING,
                451: self.MOUNTAIN_BIKING,
                461: self.MOUNTAIN_BIKING,
                463: self.MOUNTAIN_BIKING,
                448: self.MOUNTAIN_BIKING,
                450: self.MOUNTAIN_BIKING,
                460: self.MOUNTAIN_BIKING,
                449: self.MOUNTAIN_BIKING,
                464: self.MOUNTAIN_BIKING,
                459: self.MOUNTAIN_BIKING,

                24: self.HIKING,
                177: self.HIKING,
                109: self.HIKING,
                32: self.HIKING,
                508: self.HIKING,
                510: self.HIKING,
                509: self.HIKING,
                220: self.HIKING,
                114: self.HIKING,
                22: self.HIKING,
                234: self.HIKING,


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
            self.duration = aggregates.get('active_time_total')

            #preserve the timezone entered by the user in MapMyFitness
            activityTimezone = pytz.timezone(activity.get('start_locale_timezone'))
            self.date = activityTimezone.normalize(parser.parse(activity.get('start_datetime')).astimezone(pytz.utc))

            self.calories = aggregates.get('metabolic_energy_total', 0) / float(4180)
            self.distance = aggregates.get('distance_total')
            self.hasGPS = activity.get('has_time_series') or activity.get('is_verified')
        elif service == Integration.STRAVA:
            types = {
                "AlpineSki": "Downhill Skiing",
                "BackcountrySki": "Cross-Country Skiing",
                "Hike": "Hiking",
                "IceSkate": "Skating",
                "InlineSkate": "Skating",
                "Kitesurf": "Other",
                "NordicSki": "Cross-Country Skiing",
                "Ride": "Cycling",
                "RollerSki": "Other",
                "Run": "Running",
                "Snowboard": "Snowboarding",
                "Snowshoe": "Nordic Walking",
                "Swim": "Swimming",
                "Walk": "Walking",
                "Windsurf": "Other",
                "Workout": "Other"
            }

            self.type = types.get(activity.get('type'), "Other")
            self.uri = "http://www.strava.com/activities/%s" % activity.get('id')
            self.duration = activity.get('moving_time')

            self.date = activity.get('start_date')

            #not available in activity summary form from strava :(
            self.calories = None

            self.distance = activity.get('distance')
            self.hasGPS = not activity.get('manual')

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

    def hasTokens(self):
        return self.user.runkeeperToken is not None and len(self.user.runkeeperToken) > 0

    def getFitnessActivities(self, noEarlierThan=None, noLaterThan=None, modifiedSince=None, url=None):
        params = {
            'access_token': self.user.runkeeperToken,
            'pageSize': 1000,
        }

        if url is None:
            if noEarlierThan is not None:
                params['noEarlierThan'] = noEarlierThan.strftime('%Y-%m-%d')

            if noLaterThan is not None:
                params['noLaterThan'] = noLaterThan.strftime('%Y-%m-%d')

            headers = {}

            if modifiedSince is not None:
                headers['If-Modified-Since'] = modifiedSince.strftime('%a, %d %b %Y %H:%M:%S GMT')

            url = "%s%s" % (self.RUNKEEPER_API_URL, self.FITNESS_ACTIVITIES)
            r = requests.get(url, params=params, headers=headers)
        else:
            url = "%s%s" % (self.RUNKEEPER_API_URL, url)
            r = requests.get(url, params=params)

        more = {'hasMore': False, 'url': None}

        if r.status_code == 304:
            # status = 304 ~ not modified
            return [], more
        elif r.status_code != 200:
            raise ExternalIntegrationException("Status Code: %s" % r.status_code, status_code=r.status_code)

        result = r.json()

        next = result.get('next', None)
        if next is not None:
            more = {'hasMore': True, 'url': next}

        return result.get('items', []), more

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

    def hasTokens(self):
        return self.user.mapmyfitnessToken is not None and len(self.user.mapmyfitnessToken) > 0

    def getOutput(self, json):
        return json.get('result').get('output')

    def getFitnessActivities(self, noEarlierThan=None, noLaterThan=None, modifiedSince=None, url=None):
        if url is not None:
            r = requests.get('%s%s' % (self.API_URL, url), auth=self.oauth)
        else:
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

            r = requests.get('%s/v7.1/workout/' % self.API_URL, auth=self.oauth, params=params)

        if r.status_code != 200:
            raise ExternalIntegrationException("Status Code: %s" % r.status_code, status_code=r.status_code)

        result = r.json()
        next = result.get('_links').get('next', [])

        if len(next) > 0:
            more = {'hasMore': True, 'url': next[0].get('href')}
        else:
            more = {'hasMore': False, 'url': None}

        return result.get('_embedded').get('workouts'), more

    def getUserProfile(self):
        r = requests.get('%s/v7.1/user/self/' % self.API_URL, auth=self.oauth)

        if r.status_code != 200:
            raise ExternalIntegrationException("Status Code: %s" % r.status_code, status_code=r.status_code)

        profile = r.json()

        r = requests.get('%s/v7.1/user_profile_photo/%s/' % (self.API_URL, profile.get('id')), auth=self.oauth)

        if r.status_code != 200:
            raise ExternalIntegrationException("Status Code: %s" % r.status_code, status_code=r.status_code)

        profile['photos'] = r.json()['_links']

        return Profile(profile, service=Integration.MAPMYFITNESS)

    def getActivityTypes(self, url='/v7.1/activity_type/'):
        r = requests.get('%s%s' % (self.API_URL, url), auth=self.oauth, params={
            'limit': 1000
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


class StravaService(object):
    API_URL = 'https://www.strava.com/api/v3'

    def __init__(self, user):
        self.user = user
        super(StravaService, self).__init__()

    def hasTokens(self):
        return self.user.stravaToken is not None and len(self.user.stravaToken) > 0

    def getFitnessActivity(self, activityID):
        params = {
            'access_token': self.user.stravaToken
        }
        headers = {}

        url = "%s/activities/%s" % (self.API_URL, activityID)
        r = requests.get(url, params=params, headers=headers)

        if r.status_code != 200:
            raise ExternalIntegrationException("Status Code: %s" % r.status_code, status_code=r.status_code)

        return r.json()


    def getFitnessActivities(self, noEarlierThan=None, noLaterThan=None, modifiedSince=None, url=None):
        params = {
            'access_token': self.user.stravaToken,
            "per_page": 200,
        }
        # before, after, page, per_page

        if noEarlierThan is not None:
            params['after'] = unix_time(noEarlierThan)

        if noLaterThan is not None:
            params['before'] = unix_time(noLaterThan)

        headers = {}

        url = "%s/athlete/activities" % self.API_URL
        r = requests.get(url, params=params, headers=headers)

        more = {'hasMore': False, 'url': None}

        if r.status_code == 304:
            # status = 304 ~ not modified
            return [], more
        elif r.status_code != 200:
            raise ExternalIntegrationException("Status Code: %s" % r.status_code, status_code=r.status_code)

        result = r.json()
        return result, more

    def getUserProfile(self):
        params = {
            'access_token': self.user.stravaToken,
        }

        url = "%s/athlete" % self.API_URL
        r = requests.get(url, params=params)

        if r.status_code != 200:
            raise ExternalIntegrationException("Status Code: %s" % r.status_code, status_code=r.status_code)

        return Profile(r.json(), service=Integration.STRAVA)


