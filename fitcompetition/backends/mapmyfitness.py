import urlparse
from django.utils import simplejson

from social_auth.backends import ConsumerBasedOAuth, OAuthBackend
from social_auth.exceptions import AuthCanceled
from social_auth.utils import setting

MAPMYFITNESS_SERVER = 'mapmyfitness.com'
MAPMYFITNESS_API = 'api.%s/3.1' % MAPMYFITNESS_SERVER
MAPMYFITNESS_REQUEST_TOKEN_URL = 'http://%s/oauth/request_token' % MAPMYFITNESS_API
MAPMYFITNESS_ACCESS_TOKEN_URL = 'http://%s/oauth/access_token' % MAPMYFITNESS_API
MAPMYFITNESS_AUTHORIZATION_URL = 'https://%s/oauth/authorize' % MAPMYFITNESS_SERVER


#request token and secret provided by map my fitness
#user approves access
# request an access token and secret from map my fitness to replace the request token and secret
#use access token to access mmf resources

class MapMyFitnessBackend(OAuthBackend):
    name = 'mapmyfitness'
    EXTRA_DATA = [
        ('id', 'id'),
        ('expires', 'expires')
    ]

    def get_user_details(self, response):
        user = response.get('user').get('result').get('output').get('user')

        token_credentials = urlparse.parse_qs(response.get('access_token'))

        token = token_credentials.get('oauth_token')[0]
        tokenSecret = token_credentials.get('oauth_token_secret')[0]

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
    AUTHORIZATION_URL = MAPMYFITNESS_AUTHORIZATION_URL
    REQUEST_TOKEN_URL = MAPMYFITNESS_REQUEST_TOKEN_URL
    ACCESS_TOKEN_URL = MAPMYFITNESS_ACCESS_TOKEN_URL
    AUTH_BACKEND = MapMyFitnessBackend
    SETTINGS_KEY_NAME = 'MAPMYFITNESS_CLIENT_ID'
    SETTINGS_SECRET_NAME = 'MAPMYFITNESS_CLIENT_SECRET'

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        url = 'http://' + MAPMYFITNESS_API + '/users/get_user?o=json'
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

        return setting('MAPMYFITNESS_CLIENT_ID') and setting('MAPMYFITNESS_CLIENT_SECRET')


# Backend definition
BACKENDS = {
    'mapmyfitness': MapMyFitnessAuth,
}
