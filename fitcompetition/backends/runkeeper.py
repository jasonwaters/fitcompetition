from urllib import urlencode

from django.utils import simplejson

from social_auth.backends import BaseOAuth2, OAuthBackend
from social_auth.utils import dsa_urlopen

RUNKEEPER_AUTHORIZATION_URL = 'https://runkeeper.com/apps/authorize'
RUNKEEPER_DEAUTHORIZATION_URL = 'https://runkeeper.com/apps/de-authorize'
RUNKEEPER_ACCESS_TOKEN_URL = 'https://runkeeper.com/apps/token'

RUNKEEPER_API_URL = 'https://api.runkeeper.com'
RUNKEEPER_USER_RESOURCE = '/user'
RUNKEEPER_PROFILE_RESOURCE = '/profile'


class RunkeeperBackend(OAuthBackend):
    name = 'runkeeper'

    @classmethod
    def extra_data(cls, user, uid, response, details=None):
        """Return access_token and extra defined names to store in
        extra_data field"""
        data = super(RunkeeperBackend, cls).extra_data(user, uid, response,
                                                       details)
        try:
            data['username'] = response['user']['userID']
            data['gender'] = response['profile']['gender']
            data['profile_url'] = response['profile']['profile']
            data['medium_picture'] = response['profile']['medium_picture']
            data['normal_picture'] = response['profile']['normal_picture']
        except KeyError:
            pass
        return data

    def get_user_id(self, details, response):
        return response['user']['userID']

    def get_user_details(self, response):
        """Return user details from RUNKEEPER account"""
        username = response['user']['userID']
        fullname = response['profile'].get('name', '')

        if fullname:
            try:  # Try to split name for django user storage
                first_name, last_name = fullname.rsplit(' ', 1)
            except ValueError:
                first_name = fullname

        token = response['access_token']

        return {
            'username': username,
            'email': '%s@runkeeper.com' % username,
            # 'fullname': fullname,
            # 'runkeeperToken': token,
            'first_name': first_name,
            'last_name': last_name
        }


class RunkeeperAuth(BaseOAuth2):
    """RUNKEEPER OAuth mechanism"""
    AUTHORIZATION_URL = RUNKEEPER_AUTHORIZATION_URL
    ACCESS_TOKEN_URL = RUNKEEPER_ACCESS_TOKEN_URL
    AUTH_BACKEND = RunkeeperBackend
    SETTINGS_KEY_NAME = 'RUNKEEPER_CLIENT_ID'
    SETTINGS_SECRET_NAME = 'RUNKEEPER_CLIENT_SECRET'

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""

        url = "%s%s?%s" % (RUNKEEPER_API_URL, RUNKEEPER_USER_RESOURCE, urlencode({'access_token': access_token}))

        try:
            user_data = simplejson.load(dsa_urlopen(url))
        except ValueError:
            user_data = None

        if user_data:
            url = "%s%s?%s" % (RUNKEEPER_API_URL, RUNKEEPER_PROFILE_RESOURCE, urlencode({'access_token': access_token}))
            try:
                profile_data = simplejson.load(dsa_urlopen(url))
            except ValueError:
                profile_data = None

        return {
            'user': user_data,
            'profile': profile_data
        }


# Backend definition
BACKENDS = {
    'runkeeper': RunkeeperAuth,
}