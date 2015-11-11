import datetime
from django.test import TestCase
from fitcompetition.models import FitUser, Account, Challenge
from fitcompetition.settings import TIME_ZONE
import pytz
import uuid


class AccountCreationTests(TestCase):
    def test_user_account(self):
        user = FitUser.objects.create(username='alf',
                                      first_name='alf',
                                      last_name='doe',
                                      email='alf@pluto.net',
                                      is_staff=False,
                                      fullname="Alf")

        self.assertEqual("Alf", user.fullname, "Name should be 'Alf'")

        try:
            self.assertIsNotNone(user.account, "Account for user was not created")
        except Account.DoesNotExist:
            self.assertTrue(False, "Account for user was not created")

    def test_challenge_account(self):
        challenge = Challenge.objects.create(name="Marathon",
                                             slug=uuid.uuid4(),
                                             type="INDV",
                                             style="ALL",
                                             distance=100,
                                             startdate=datetime.datetime(2013, 11, 16).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             enddate=datetime.datetime(2014, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             ante=25)

        try:
            self.assertIsNotNone(challenge.account, "Account for challenge was not created")
        except Account.DoesNotExist:
            self.assertTrue(False, "Account for challenge was not created")
