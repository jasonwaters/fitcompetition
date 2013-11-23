"""
Run "manage.py test".
"""
import datetime

from django.test import TestCase
from fitcompetition.models import FitUser, Account, Challenge, ActivityType, Transaction, FitnessActivity
from fitcompetition.settings import TIME_ZONE
from fitcompetition.templatetags.apptags import toMeters
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
                                             type="INDV",
                                             style="ALL",
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
                                                  type="INDV",
                                                  style="ALL",
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


class ReconciliationTests(TestCase):
    def setUp(self):
        self.running, created = ActivityType.objects.get_or_create(name='Running')

        self.user1 = FitUser.objects.create(username='user1',
                                            first_name='user',
                                            last_name='one',
                                            email='a@a.net',
                                            is_staff=False,
                                            fullname="user one")

        self.user2 = FitUser.objects.create(username='user2',
                                            first_name='user',
                                            last_name='two',
                                            email='b@a.net',
                                            is_staff=False,
                                            fullname="user two")

        self.user3 = FitUser.objects.create(username='user3',
                                            first_name='user',
                                            last_name='three',
                                            email='c@a.net',
                                            is_staff=False,
                                            fullname="user three")

        self.user4 = FitUser.objects.create(username='user4',
                                            first_name='user',
                                            last_name='four',
                                            email='d@a.net',
                                            is_staff=False,
                                            fullname="user four")

        FitnessActivity.objects.create(user=self.user1,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(50))

        FitnessActivity.objects.create(user=self.user1,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(60))

        FitnessActivity.objects.create(user=self.user2,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(10))

    def tearDown(self):
        pass

    def testIndividualAllCanWin(self):
        challenge = Challenge.objects.create(name="Marathon",
                                             type="INDV",
                                             style="ALL",
                                             distance=100,
                                             startdate=datetime.datetime(2013, 1, 1).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             enddate=datetime.datetime(2013, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             ante=25)

        challenge.approvedActivities.add(self.running)

        challenge.addChallenger(self.user1)
        challenge.addChallenger(self.user2)

        Transaction.objects.deposit(self.user1.account, 25)
        Transaction.objects.deposit(self.user2.account, 25)

        self.assertEqual(50, challenge.account.balance)

        challenge.performReconciliation()

        self.assertEqual(0, challenge.account.balance)

        self.assertEqual(50, self.user1.account.balance)
        self.assertEqual(0, self.user2.account.balance)

    def testIndividualWinnerTakesAll(self):
        pass

    def testTeamAllCanWin(self):
        pass

    def testTeamWinnerTakesAll(self):
        pass