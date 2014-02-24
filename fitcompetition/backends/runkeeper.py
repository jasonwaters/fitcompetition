from fitcompetition.services import Integration
from social.backends.oauth import BaseOAuth2


RUNKEEPER_API_URL = 'https://api.runkeeper.com'
RUNKEEPER_USER_RESOURCE = '/user'
RUNKEEPER_PROFILE_RESOURCE = '/profile'


class RunkeeperOauth2(BaseOAuth2):
    name = 'runkeeper'
    AUTHORIZATION_URL = 'https://runkeeper.com/apps/authorize'
    ACCESS_TOKEN_URL = 'https://runkeeper.com/apps/token'
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('expires', 'expires')
    ]

    def get_user_id(self, details, response):
        return response['user']['userID']

    def get_user_details(self, response):
        username = 'rkpr_%s' % str(response['user']['userID'])

        fullname = response['profile'].get('name', '')

        if fullname:
            try:  # Try to split name for django user storage
                first_name, last_name = fullname.rsplit(' ', 1)
            except ValueError:
                if fullname is not None and len(fullname) > 0:
                    first_name = fullname
                else:
                    first_name = "Unnamed"
                last_name = ""

        token = response.get('access_token')

        gender = response['profile'].get('gender')
        profile_url = response['profile'].get('profile')
        medium_picture = response['profile'].get('medium_picture')
        normal_picture = response['profile'].get('normal_picture')

        return {
            'username': username,
            'fullname': fullname,
            'runkeeperToken': token,
            'first_name': first_name,
            'last_name': last_name,
            'gender': gender,
            'profile_url': profile_url,
            'medium_picture': medium_picture,
            'normal_picture': normal_picture,
            'integrationName': Integration.RUNKEEPER
        }

    def user_data(self, access_token, *args, **kwargs):
        user_data = self.requestRunkeeperData(access_token, RUNKEEPER_USER_RESOURCE)
        profile_data = self.requestRunkeeperData(access_token, RUNKEEPER_PROFILE_RESOURCE)

        return {
            'user': user_data,
            'profile': profile_data,
            'expires': 60 * 60 * 24 * 365
        }

    def requestRunkeeperData(self, access_token, api_endpiont):
        url = "%s%s" % (RUNKEEPER_API_URL, api_endpiont)
        return self.get_json(url, params={'access_token': access_token})
