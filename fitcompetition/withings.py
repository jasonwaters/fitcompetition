import time
import re
import requests


class WithingsService(object):
    login_url = 'https://account.withings.com/connectionwou/account_login'

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.sessionID = None

    def authenticate(self):
        result = self.session.post(self.login_url, data={
            'use_authy': '',
            'is_admin': '',
            'email': self.username,
            'password': self.password,
            })

        regx = re.compile('wiService\.sessionid.+=.+\"([a-zA-Z0-9\-]+)\";', re.MULTILINE)
        groups = regx.search(result.content).groups()

        self.sessionID = groups[0]

    def getWeightMeasurements(self, userid):
        if self.sessionID is None:
            self.authenticate()

        request_params = {
            'sessionid': self.sessionID,
            'category': 1,
            'userid': userid,
            'offset': 0,
            'limit': 400,
            'startdate': 0,  # int(time.mktime((datetime.now() - timedelta(days=90)).timetuple())),
            'enddate': int(time.time()),
            'appname': 'my2',
            'appliver': 'cfe409b6',
            'apppfm': 'web',
            'action': 'getmeas',
            'meastype': 1,  # weight
        }

        result = self.session.post('https://healthmate.withings.com/index/service/measure', request_params)
        return result.json().get('body').get('measuregrps')