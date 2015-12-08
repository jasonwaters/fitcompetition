import json
import datetime
from django.test import TestCase, Client
from fitcompetition.models import FitUser, Challenge, Transaction
import pytz
import uuid


class APITests(TestCase):

    def newChallenge(self, name, type="INDV", style="ALL", distance=100, ante=25):
        now = datetime.datetime.now(tz=pytz.utc)
        return Challenge.objects.create(name=name,
                                        slug=uuid.uuid4(),
                                        type=type,
                                        style=style,
                                        distance=distance,
                                        startdate=now,
                                        enddate=now + datetime.timedelta(days=10),
                                        ante=ante)

    def getContent(self, response):
        try:
            return json.loads(response.content)
        except ValueError:
            self.fail("Unable to parse JSON: %s" % response.content)

    def setUp(self):
        super(APITests, self).setUp()

        self.user = FitUser.objects.create(username='alf',
                                           password="pbkdf2_sha256$12000$cqeuHZqWbU2u$vuhnwLgqU6haP5d9D2Qdudld1Jpr4dmc1c52zBx7d90=",
                                           first_name='alf',
                                           last_name='doe',
                                           email='alf@pluto.net',
                                           is_staff=False,
                                           fullname="Alf")

        self.client = Client()
        self.auth = self.client.login(username='alf', password='user')

    def test_join_challenge_bad_params(self):
        response = self.client.get('/api/join-challenge')

        self.assertEqual(200, response.status_code)

        content = self.getContent(response)
        self.assertFalse(content.get('success'))

        response = self.client.get('/api/join-challenge', {
            'challengeID': -1
        })
        self.assertEqual(200, response.status_code)

        content = self.getContent(response)
        self.assertFalse(content.get('success'))

    def test_join_challenge_insufficient_funds(self):
        challenge = self.newChallenge("Foo")

        response = self.client.get('/api/join-challenge', {
            'challengeID': challenge.id
        })
        self.assertEqual(200, response.status_code)

        content = self.getContent(response)
        self.assertFalse(content.get('success'))

    def test_join_challenge_sufficient_funds(self):
        Transaction.objects.deposit(self.user.account, 25)

        challenge = self.newChallenge("Foo")

        response = self.client.get('/api/join-challenge', {
            'challengeID': challenge.id
        })
        self.assertEqual(200, response.status_code)

        content = self.getContent(response)
        self.assertTrue(content.get('success'))

    def test_withdraw_challenge(self):
        Transaction.objects.deposit(self.user.account, 25)

        challenge = self.newChallenge("Foo")
        challenge.addChallenger(self.user)

        response = self.client.get('/api/withdraw-challenge', {
            'challengeID': challenge.id
        })
        self.assertEqual(200, response.status_code)

        content = self.getContent(response)
        self.assertTrue(content.get('success'))

    def test_update_user_details(self):
        response = self.client.post('/api/update-user-details', {
            'emailAddress': 'not@valid.net'
        })
        self.assertEqual(200, response.status_code)

        content = self.getContent(response)
        self.assertTrue(content.get('success'))

    def test_charge_card(self):
        response = self.client.get('/api/charge-card')
        self.assertEqual(200, response.status_code)

        content = self.getContent(response)
        self.assertFalse(content.get('success'))

    def test_stripe_customer(self):
        response = self.client.get('/api/stripe-customer')
        self.assertEqual(200, response.status_code)
        content = self.getContent(response)
        self.assertFalse(content.get('success'))

    def test_stripe_card(self):
        response = self.client.get('/api/del-stripe-card')
        self.assertEqual(200, response.status_code)
        content = self.getContent(response)
        self.assertFalse(content.get('success'))
