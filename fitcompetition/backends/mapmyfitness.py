from fitcompetition.services import Integration
from social.backends.oauth import BaseOAuth1


class MapMyFitnessOAuth(BaseOAuth1):
    name = 'mapmyfitness'

    EXTRA_DATA = [
        ('expires', 'expires')
    ]

    AUTHORIZATION_URL = 'https://www.mapmyfitness.com/oauth/authorize/'

    REQUEST_TOKEN_URL = 'https://api.mapmyapi.com/v7.0/oauth/temporary_credential/'
    REQUEST_TOKEN_METHOD = 'POST'

    ACCESS_TOKEN_URL = 'https://api.mapmyapi.com/v7.0/oauth/token_credential/'
    ACCESS_TOKEN_METHOD = 'POST'

    MMF_BASE_URL = 'http://mapmyfitness.com'

    def get_user_id(self, details, response):
        return response['user']['id']

    def get_user_details(self, response):
        user = response.get('user')

        token = response.get('access_token').get('oauth_token')
        tokenSecret = response.get('access_token').get('oauth_token_secret')

        images = user.get('_links').get('image')
        imageMap = {}
        for image in images:
            imageMap[image.get('name')] = image.get('href')

        return {
            'username': 'mmf_%s' % str(user.get('id')),
            'email': user.get('email'),
            'fullname': '%s' % (user.get('display_name')),
            'mapmyfitnessToken': token,
            'mapmyfitnessTokenSecret': tokenSecret,
            'first_name': user.get('first_name'),
            'last_name': user.get('last_name'),
            'gender': user.get('gender'),
            'profile_url': "http://www.mapmyfitness.com/profile/%s/" % str(user.get('id')),
            'medium_picture': '%s%s' % (self.MMF_BASE_URL, imageMap.get('medium')),
            'normal_picture': '%s%s' % (self.MMF_BASE_URL, imageMap.get('large')),
            'integrationName': Integration.MAPMYFITNESS
        }

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        user_data = self.get_json('https://api.mapmyapi.com/api/0.1/user/%s/' % access_token.get('user_id'), auth=self.oauth_auth(access_token))
        return {
            'user': user_data,
            'expires': 60 * 60 * 24 * 365
        }