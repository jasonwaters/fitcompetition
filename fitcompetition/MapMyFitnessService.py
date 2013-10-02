import requests
from requests_oauthlib import OAuth1
from django.conf import settings


class MapMyFitnessService:
    def __init__(self, user):
        self.user = user
        self.oauth = OAuth1(getattr(settings, 'MAPMYFITNESS_CLIENT_ID'),
                            getattr(settings, 'MAPMYFITNESS_CLIENT_SECRET'),
                            unicode(user.mapmyfitnessToken),
                            unicode(user.mapmyfitnessTokenSecret),
                            signature_type='QUERY')

    def getOutput(self, json):
        return json.get('result').get('output')

    def getUser(self):
        r = requests.get('http://api.mapmyfitness.com/3.1/users/get_user', auth=self.oauth)
        json = r.json()
        return self.getOutput(json).get('user')

    def getFitnessActivities(self):
        r = requests.get('http://api.mapmyfitness.com/3.1/workouts/get_workouts', auth=self.oauth)
        json = r.json()
        return self.getOutput(json).get('workouts')

    def getActivityTypes(self):
        r = requests.get('http://api.mapmyfitness.com/3.1/workouts/get_activity_types', auth=self.oauth)
        json = r.json()
        return self.getOutput(json)
