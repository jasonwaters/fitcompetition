from fitcompetition.services import Integration
from social.backends.oauth import BaseOAuth2


class StravaOAuth(BaseOAuth2):
    name = 'strava'

    EXTRA_DATA = [
        ('expires', 'expires')
    ]

    AUTHORIZATION_URL = 'https://www.strava.com/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://www.strava.com/oauth/token'
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False

    def get_user_id(self, details, response):
        return response['athlete']['id']

    def get_user_details(self, response):
        token = response.get('access_token')

        athlete = response['athlete']

        first_name = athlete.get('firstname', '')
        last_name = athlete.get('lastname', '')

        return {
            'username': "strv_%s" % athlete.get('id'),
            'email': athlete.get('email', ''),
            'fullname': "%s %s" % (first_name, last_name),
            'stravaToken': token,
            'first_name': first_name,
            'last_name': last_name,
            'gender': athlete.get('sex'),
            'profile_url': "http://www.strava.com/athletes/%s" % athlete.get('id'),
            'medium_picture': athlete.get('profile_medium') if "medium.png" not in athlete.get('profile_medium') else None,
            'normal_picture': athlete.get('profile') if "large.png" not in athlete.get('profile') else None,
            'integrationName': Integration.STRAVA
        }

    def user_data(self, access_token, *args, **kwargs):
        response = self.get_json('https://www.strava.com/api/v3/athlete', params={'access_token': access_token})
        response['expires'] = 60 * 60 * 24 * 365
        return response