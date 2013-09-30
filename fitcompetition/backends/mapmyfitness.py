import re
from django.utils import simplejson

from social_auth.backends import ConsumerBasedOAuth, OAuthBackend
from social_auth.exceptions import AuthCanceled
from social_auth.utils import setting

MAPMYFITNESS_SERVER = 'mapmyfitness.com'
MAPMYFITNESS_API = 'api.%s/3.1' % MAPMYFITNESS_SERVER
MAPMYFITNESS_REQUEST_TOKEN_URL = 'http://%s/oauth/request_token' % MAPMYFITNESS_API
MAPMYFITNESS_ACCESS_TOKEN_URL = 'http://%s/oauth/access_token' % MAPMYFITNESS_API
MAPMYFITNESS_AUTHORIZATION_URL = 'https://%s/oauth/authorize' % MAPMYFITNESS_SERVER


class MapMyFitnessBackend(OAuthBackend):
    """Twitter OAuth authentication backend"""
    name = 'mapmyfitness'
    EXTRA_DATA = [
        ('id', 'id'),
        ('expires', 'expires')
    ]

    def get_user_details(self, response):
        """Return user details from Dropbox account"""
        user = response.get('user').get('result').get('output').get('user')

        validToken = re.compile('^oauth_token_secret=(.+)&oauth_token=(.+)$')
        matches = validToken.match(response.get('access_token'))
        if matches:
            token = matches.group(1)
            tokenSecret = matches.group(2)
        else:
            token = None
            tokenSecret = None

        result = {
            'username': 'mmf_%s' % user.get('user_id'),
            'email': user.get('email'),
            'fullname': '%s %s' % (user.get('first_name'), user.get('last_name')),
            'mapmyfitnessToken': token,
            'mapmyfitnessTokenSecret': tokenSecret,
            'first_name': user.get('first_name'),
            'last_name': user.get('last_name'),
            'gender': user.get('sex'),
            'profile_url': 'http://%s%s' % (MAPMYFITNESS_SERVER, user.get('profile_link')),
            'medium_picture': None,
            'normal_picture': None
        }

        return result

    def get_user_id(self, details, response):
        user = response.get('user').get('result').get('output').get('user')
        return user.get('user_id')


class MapMyFitnessAuth(ConsumerBasedOAuth):
    """Twitter OAuth authentication mechanism"""
    AUTHORIZATION_URL = MAPMYFITNESS_AUTHORIZATION_URL
    REQUEST_TOKEN_URL = MAPMYFITNESS_REQUEST_TOKEN_URL
    ACCESS_TOKEN_URL = MAPMYFITNESS_ACCESS_TOKEN_URL
    AUTH_BACKEND = MapMyFitnessBackend
    SETTINGS_KEY_NAME = 'MAPMYFITNESS_CLIENT_ID'
    SETTINGS_SECRET_NAME = 'MAPMYFITNESS_CLIENT_SECRET'

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        url = 'http://' + MAPMYFITNESS_API + '/users/get_user'
        request = self.oauth_request(access_token, url)
        response = self.fetch_response(request)

        try:
            user_data = simplejson.loads(response)
        except ValueError:
            user_data = None

        return {
            'user': user_data,
            'expires': 60 * 60 * 24 * 365
        }

    def auth_complete(self, *args, **kwargs):
        """Completes login process, must return user instance"""
        if 'error' in self.data:
            raise AuthCanceled(self)
        else:
            return super(MapMyFitnessAuth, self).auth_complete(*args, **kwargs)

    @classmethod
    def enabled(cls):
        """Return backend enabled status by checking basic settings"""

        return setting('MAPMYFITNESS_CLIENT_ID') \
            and setting('MAPMYFITNESS_CLIENT_SECRET')


# Backend definition
BACKENDS = {
    'mapmyfitness': MapMyFitnessAuth,
}
