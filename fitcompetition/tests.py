"""
Run "manage.py test".
"""
import datetime

from django.test import TestCase
from fitcompetition.models import FitUser, Account, Challenge, ActivityType, Transaction
from fitcompetition.settings import TIME_ZONE
import pytz


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
            account = Account.objects.get(user=user)
            self.assertIsNotNone(account, "Account for user was not created")
            self.assertIsNone(account.challenge, "User accounts should not be tied to a challenge")
            self.assertEqual(user.account, account)
        except Account.DoesNotExist:
            self.assertTrue(False, "Account for user was not created")

    def test_challenge_account(self):
        challenge = Challenge.objects.create(name="Marathon",
                                             type="SIMP",
                                             distance=100,
                                             startdate=datetime.datetime(2013, 11, 16).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             enddate=datetime.datetime(2014, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             ante=25)

        try:
            account = Account.objects.get(challenge=challenge)
            self.assertIsNotNone(account, "Account for challenge was not created")
            self.assertIsNone(account.user, "Challenge accounts should not be tied to a user")
            self.assertEqual(challenge.account, account)
        except Account.DoesNotExist:
            self.assertTrue(False, "Account for challenge was not created")


class TransactionTests(TestCase):
    def setUp(self):
        self.user = FitUser.objects.create(username='alf',
                                           first_name='alf',
                                           last_name='doe',
                                           email='alf@pluto.net',
                                           is_staff=False,
                                           fullname="Alf")

        self.challenge = Challenge.objects.create(name="Marathon",
                                                  type="SIMP",
                                                  distance=100,
                                                  startdate=datetime.datetime(2013, 11, 16).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                                  enddate=datetime.datetime(2014, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                                  ante=25)

    def tearDown(self):
        pass

    def testChallengeMembership(self):
        now = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE))

        self.challenge.addChallenger(self.user)

        self.assertEqual(25, self.challenge.account.balance, "Transaction for challenge was not created")
        self.assertEqual(-25, self.user.account.balance, "Transaction for user was not created")

        Transaction.objects.create(date=now,
                                   account=self.user.account,
                                   description="",
                                   amount=25)

        self.assertEqual(0, self.user.account.balance, "Incorrect balance for user")

        self.challenge.removeChallenger(self.user, force=True)

        self.assertEqual(0, self.challenge.account.balance, "Transaction for challenge was not created on user withdrawal.")
        self.assertEqual(25, self.user.account.balance, "Transaction for user was not created on user withdrawal.")
