import datetime
from django.test import TestCase
from fitcompetition.models import FitUser, Challenge, Transaction
from fitcompetition.settings import TIME_ZONE
import pytz
import uuid


class TransactionTests(TestCase):
    def setUp(self):
        self.user = FitUser.objects.create(username='alf',
                                           first_name='alf',
                                           last_name='doe',
                                           email='alf@pluto.net',
                                           is_staff=False,
                                           fullname="Alf")

        self.challenge = Challenge.objects.create(name="Marathon",
                                                  slug=uuid.uuid4(),
                                                  type="INDV",
                                                  style="ALL",
                                                  distance=100,
                                                  startdate=datetime.datetime(2013, 11, 16).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                                  enddate=datetime.datetime(2014, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                                  ante=25)

    def tearDown(self):
        pass

    def testChallengeMembership(self):
        self.challenge.addChallenger(self.user)

        self.assertEqual(25, self.challenge.account.balance, "Transaction for challenge was not created")
        self.assertEqual(-25, self.user.account.balance, "Transaction for user was not created")

        Transaction.objects.deposit(self.user.account, 25)

        self.assertEqual(0, self.user.account.balance, "Incorrect balance for user")

        self.challenge.removeChallenger(self.user, force=True)

        self.assertEqual(0, self.challenge.account.balance, "Transaction for challenge was not created on user withdrawal.")
        self.assertEqual(25, self.user.account.balance, "Transaction for user was not created on user withdrawal.")

    def testBalance(self):
        self.assertEqual(0, self.user.account.balance)

        t = Transaction.objects.deposit(self.user.account, 3)

        self.assertEqual(3, t.balance)
        self.assertEqual(3, self.user.account.balance)

        t = Transaction.objects.deposit(self.user.account, 9)

        self.assertEqual(12, t.balance)
        self.assertEqual(12, self.user.account.balance)

        t = Transaction.objects.deposit(self.user.account, -10)

        self.assertEqual(2, t.balance)
        self.assertEqual(2, self.user.account.balance)

        t = Transaction.objects.deposit(self.user.account, 35)

        self.assertEqual(37, t.balance)
        self.assertEqual(37, self.user.account.balance)

        t = Transaction.objects.deposit(self.user.account, -50)

        self.assertEqual(-13, t.balance)
        self.assertEqual(-13, self.user.account.balance)

        t = Transaction.objects.deposit(self.user.account, 100)

        self.assertEqual(87, t.balance)
        self.assertEqual(87, self.user.account.balance)

        t.amount = 31
        t.save()

        self.assertEqual(18, t.balance)
        self.assertEqual(18, self.user.account.balance)
