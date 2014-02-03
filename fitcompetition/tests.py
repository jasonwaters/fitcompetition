"""
Run "manage.py test".
"""
import datetime
from decimal import Decimal
import json
from django.core import mail
from django.test import TestCase, Client
from fitcompetition import tasks
from fitcompetition.models import FitUser, Account, Challenge, ActivityType, Transaction, FitnessActivity, Team
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


class EmailTests(TestCase):
    def setUp(self):
        self.running, created = ActivityType.objects.get_or_create(name='Running')

        self.user1 = FitUser.objects.create(username='alf',
                                            password="pbkdf2_sha256$12000$cqeuHZqWbU2u$vuhnwLgqU6haP5d9D2Qdudld1Jpr4dmc1c52zBx7d90=",
                                            first_name='alf',
                                            last_name='doe',
                                            email='alf@pluto.net',
                                            is_staff=False,
                                            fullname="Alf")

        self.user2 = FitUser.objects.create(username='elmo',
                                            password="pbkdf2_sha256$12000$cqeuHZqWbU2u$vuhnwLgqU6haP5d9D2Qdudld1Jpr4dmc1c52zBx7d90=",
                                            first_name='elmo',
                                            last_name='love',
                                            email='elmo@sesame.net',
                                            is_staff=False,
                                            fullname="Elmo")

        self.challenge = Challenge.objects.create(name="Marathon",
                                                  type="INDV",
                                                  style="ALL",
                                                  distance=100,
                                                  startdate=datetime.datetime(2013, 11, 16).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                                  enddate=datetime.datetime(2014, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                                  ante=25)

    def testEmailConfirm(self):
        pass

    def testJoinChallenge(self):
        # now = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE))

        self.challenge.addChallenger(self.user1)

        self.assertEqual(1, len(mail.outbox), "Joined Challenge Email Failed To Send")
        self.assertEqual('You joined "%s"' % self.challenge.name, mail.outbox[0].subject, "Joined Challenge Email Failed To Send")
        mail.outbox = []

        self.challenge.removeChallenger(self.user1, force=True)

        self.assertEqual(0, len(mail.outbox), "No transactional email should be sent when a user withdraws from a challenge.")

    def testCashOut(self):
        c = Client()
        auth = c.login(username='alf', password='user')
        self.assertTrue(auth, 'failed to authenticate alf/user')
        response = c.post('/account-cash-out/', {
            'emailAddress': "jake@jones.net",
            'cashValue': '100'
        })

        self.assertEqual(200, response.status_code)
        try:
            value = json.loads(response.content)
            self.assertTrue(value.get('success'), "Cash Out request failed to return success:True")
        except ValueError:
            self.fail("Unable to parse JSON: %s" % response.content)

        self.assertEqual(2, len(mail.outbox), "two emails were not sent when user cashed out")

    def testDeposit(self):
        Transaction.objects.deposit(self.user1.account, 25)

        self.assertEqual(25, self.user1.account.balance)
        self.assertEqual(1, len(mail.outbox), "Deposit email failed to send")
        self.assertTrue("Your payment was received" in mail.outbox[0].subject, "Deposit email failed to send")
        mail.outbox = []

        Transaction.objects.withdraw(self.user1.account, 15)
        self.assertEqual(10, self.user1.account.balance)
        self.assertEqual(0, len(mail.outbox))

    def testChallengeStart(self):
        now = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE))
        self.challenge = Challenge.objects.create(name="aaa",
                                                  type="INDV",
                                                  style="ALL",
                                                  distance=100,
                                                  startdate=now,
                                                  enddate=now + datetime.timedelta(days=10),
                                                  ante=10)

        self.challenge.addChallenger(self.user1)
        self.challenge.addChallenger(self.user2)
        mail.outbox = []

        tasks.sendChallengeNotifications()

        self.assertEqual(2, len(mail.outbox), '2 challenge kick-off emails should have been sent')
        self.assertEqual("The challenge has begun!", mail.outbox[0].subject)
        self.assertEqual("The challenge has begun!", mail.outbox[1].subject)

    def testChallengeHalf(self):
        now = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE))
        self.challenge = Challenge.objects.create(name="aaa",
                                                  type="INDV",
                                                  style="ALL",
                                                  distance=100,
                                                  startdate=now + datetime.timedelta(days=-4),
                                                  enddate=now + datetime.timedelta(days=4),
                                                  ante=100)

        self.challenge.approvedActivities.add(self.running)

        self.challenge.addChallenger(self.user1)
        self.challenge.addChallenger(self.user2)

        FitnessActivity.objects.create(user=self.user1,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=now,
                                       calories=0,
                                       distance=toMeters(120))

        FitnessActivity.objects.create(user=self.user2,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=now,
                                       calories=0,
                                       distance=toMeters(50))

        mail.outbox = []

        tasks.sendChallengeNotifications()

        self.assertEqual(2, len(mail.outbox), '2 challenge half-over emails should have been sent')

        self.assertEqual("The challenge is half over!", mail.outbox[0].subject)
        self.assertTrue("120 miles" in mail.outbox[0].alternatives[0][0])
        self.assertTrue("dominate the leaderboard" in mail.outbox[0].alternatives[0][0])

        self.assertEqual("The challenge is half over!", mail.outbox[1].subject)
        self.assertTrue("50 miles" in mail.outbox[1].alternatives[0][0])
        self.assertTrue("on your way to conquer" in mail.outbox[1].alternatives[0][0])

    def testChallengeEnd(self):
        now = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE))
        self.challenge = Challenge.objects.create(name="aaa",
                                                  type="INDV",
                                                  style="ALL",
                                                  distance=100,
                                                  startdate=now + datetime.timedelta(days=-20),
                                                  enddate=now + datetime.timedelta(days=-1),
                                                  ante=100)

        self.challenge.approvedActivities.add(self.running)

        self.challenge.addChallenger(self.user1)
        self.challenge.addChallenger(self.user2)

        FitnessActivity.objects.create(user=self.user1,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=now + datetime.timedelta(days=-5),
                                       calories=0,
                                       distance=toMeters(120))

        FitnessActivity.objects.create(user=self.user2,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=now + datetime.timedelta(days=-5),
                                       calories=0,
                                       distance=toMeters(50))

        mail.outbox = []

        tasks.sendChallengeNotifications()
        self.assertEqual(2, len(mail.outbox), '2 challenge ended emails should have been sent')

        self.assertEqual("The challenge is over!", mail.outbox[0].subject)
        self.assertTrue("120 miles" in mail.outbox[0].alternatives[0][0])
        self.assertTrue("We've credited $200" in mail.outbox[0].alternatives[0][0])

        self.assertEqual("The challenge is over!", mail.outbox[1].subject)
        self.assertTrue("50 miles" in mail.outbox[1].alternatives[0][0])
        self.assertTrue("sadly you did not complete the challenge" in mail.outbox[1].alternatives[0][0])


class ChallengeTests(TestCase):
    def setUp(self):
        self.c1 = Challenge.objects.create(name="aaa",
                                           type="INDV",
                                           style="ALL",
                                           distance=100,
                                           startdate=datetime.datetime(2014, 1, 1, tzinfo=pytz.timezone(TIME_ZONE)),
                                           enddate=datetime.datetime(2014, 1, 10, tzinfo=pytz.timezone(TIME_ZONE)),
                                           ante=10)

        self.c2 = Challenge.objects.create(name="bbb",
                                           type="INDV",
                                           style="ONE",
                                           distance=100,
                                           startdate=datetime.datetime(2014, 1, 1, tzinfo=pytz.timezone(TIME_ZONE)),
                                           enddate=datetime.datetime(2014, 4, 1, tzinfo=pytz.timezone(TIME_ZONE)),
                                           ante=20)

        self.c3 = Challenge.objects.create(name="ccc",
                                           type="TEAM",
                                           style="ALL",
                                           distance=100,
                                           startdate=datetime.datetime(2014, 1, 1, tzinfo=pytz.timezone(TIME_ZONE)),
                                           enddate=datetime.datetime(2014, 1, 7, tzinfo=pytz.timezone(TIME_ZONE)),
                                           ante=30)

        self.c4 = Challenge.objects.create(name="ddd",
                                           type="TEAM",
                                           style="ONE",
                                           distance=100,
                                           startdate=datetime.datetime(2014, 2, 1, tzinfo=pytz.timezone(TIME_ZONE)),
                                           enddate=datetime.datetime(2014, 3, 1, tzinfo=pytz.timezone(TIME_ZONE)),
                                           ante=30)

    def testMidDate(self):
        self.assertEqual(datetime.datetime(2014, 1, 5, tzinfo=pytz.timezone(TIME_ZONE)).date(), self.c1.middate.date())
        self.assertEqual(datetime.datetime(2014, 2, 15, tzinfo=pytz.timezone(TIME_ZONE)).date(), self.c2.middate.date())
        self.assertEqual(datetime.datetime(2014, 1, 4, tzinfo=pytz.timezone(TIME_ZONE)).date(), self.c3.middate.date())
        self.assertEqual(datetime.datetime(2014, 2, 15, tzinfo=pytz.timezone(TIME_ZONE)).date(), self.c4.middate.date())

    def testDuration(self):
        self.assertEqual(10, self.c1.numDays)
        self.assertEqual(91, self.c2.numDays)
        self.assertEqual(7, self.c3.numDays)
        self.assertEqual(29, self.c4.numDays)


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
        self.challenge.addChallenger(self.user)

        self.assertEqual(25, self.challenge.account.balance, "Transaction for challenge was not created")
        self.assertEqual(-25, self.user.account.balance, "Transaction for user was not created")

        Transaction.objects.deposit(self.user.account, 25)

        self.assertEqual(0, self.user.account.balance, "Incorrect balance for user")

        self.challenge.removeChallenger(self.user, force=True)

        self.assertEqual(0, self.challenge.account.balance, "Transaction for challenge was not created on user withdrawal.")
        self.assertEqual(25, self.user.account.balance, "Transaction for user was not created on user withdrawal.")


class TeamTests(TestCase):
    def setUp(self):
        pass


class ReconciliationTests(TestCase):
    def setUp(self):
        self.running, created = ActivityType.objects.get_or_create(name='Running')

        self.elmo = FitUser.objects.create(username='user1',
                                           first_name='Elmo',
                                           last_name='user',
                                           email='a@a.net',
                                           is_staff=False,
                                           fullname="Elmo")

        self.count = FitUser.objects.create(username='user2',
                                            first_name='Count',
                                            last_name='Dracula',
                                            email='b@a.net',
                                            is_staff=False,
                                            fullname="Count Dracula")

        self.bert = FitUser.objects.create(username='user3',
                                           first_name='Bert',
                                           last_name='user',
                                           email='c@a.net',
                                           is_staff=False,
                                           fullname="Bert")

        self.ernie = FitUser.objects.create(username='user4',
                                            first_name='Ernie',
                                            last_name='user',
                                            email='d@a.net',
                                            is_staff=False,
                                            fullname="Ernie")

        FitnessActivity.objects.create(user=self.elmo,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(50))

        FitnessActivity.objects.create(user=self.elmo,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(70))

        FitnessActivity.objects.create(user=self.count,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(70))

        FitnessActivity.objects.create(user=self.count,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(70))

        FitnessActivity.objects.create(user=self.bert,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(20))

        FitnessActivity.objects.create(user=self.bert,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(90))

        FitnessActivity.objects.create(user=self.ernie,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(65))


        #elmo 120 miles
        #count 140 miles
        #bert 110 miles
        #ernie 65 miles

    def testChallengeNotEnded(self):
        now = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE))

        start = now - datetime.timedelta(days=7)
        end = now + datetime.timedelta(days=30)

        challenge = Challenge.objects.create(name="Marathon",
                                             type="INDV",
                                             style="ALL",
                                             distance=100,
                                             startdate=start,
                                             enddate=end,
                                             ante=25)

        challenge.approvedActivities.add(self.running)

        challenge.addChallenger(self.elmo)
        challenge.addChallenger(self.count)
        challenge.addChallenger(self.bert)
        challenge.addChallenger(self.ernie)

        Transaction.objects.deposit(self.elmo.account, 25)
        Transaction.objects.deposit(self.count.account, 25)
        Transaction.objects.deposit(self.bert.account, 25)
        Transaction.objects.deposit(self.ernie.account, 25)

        self.assertEqual(100, challenge.account.balance)

        self.assertEqual(0, self.elmo.account.balance)
        self.assertEqual(0, self.count.account.balance)
        self.assertEqual(0, self.bert.account.balance)
        self.assertEqual(0, self.ernie.account.balance)

        challenge.performReconciliation()

        self.assertEqual(100, challenge.account.balance)

        self.assertEqual(0, self.elmo.account.balance)
        self.assertEqual(0, self.count.account.balance)
        self.assertEqual(0, self.bert.account.balance)
        self.assertEqual(0, self.ernie.account.balance)

        self.assertEqual(challenge.numWinners, 0)
        self.assertAlmostEqual(challenge.disbursementAmount, 0, 2)
        self.assertFalse(challenge.reconciled)

    def testIndividualAllCanWin(self):
        challenge = Challenge.objects.create(name="Marathon",
                                             type="INDV",
                                             style="ALL",
                                             distance=100,
                                             startdate=datetime.datetime(2013, 1, 1).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             enddate=datetime.datetime(2013, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             ante=25)

        challenge.approvedActivities.add(self.running)

        challenge.addChallenger(self.elmo)
        challenge.addChallenger(self.count)
        challenge.addChallenger(self.bert)
        challenge.addChallenger(self.ernie)

        self.assertEqual(4, len(mail.outbox))
        mail.outbox = []

        Transaction.objects.deposit(self.elmo.account, 25)
        Transaction.objects.deposit(self.count.account, 25)
        Transaction.objects.deposit(self.bert.account, 25)

        self.assertEqual(3, len(mail.outbox))
        mail.outbox = []

        self.assertEqual(100, challenge.account.balance)

        self.assertEqual(0, self.elmo.account.balance)
        self.assertEqual(0, self.count.account.balance)
        self.assertEqual(0, self.bert.account.balance)
        self.assertEqual(-25, self.ernie.account.balance)

        challenge.performReconciliation()

        self.assertAlmostEqual(Decimal(0.01), challenge.account.balance, 2)

        # $100 / 3 winners = 33.33
        self.assertAlmostEqual(Decimal(33.33), self.elmo.account.balance, 2)
        self.assertAlmostEqual(Decimal(33.33), self.count.account.balance, 2)
        self.assertAlmostEqual(Decimal(33.33), self.bert.account.balance, 2)
        self.assertEqual(-25, self.ernie.account.balance)

        self.assertEqual(challenge.numWinners, 3)
        self.assertAlmostEqual(challenge.disbursementAmount, Decimal(33.33), 2)
        self.assertAlmostEqual(challenge.totalDisbursed, Decimal(99.99), 2)

        self.assertEqual(0, len(mail.outbox))

    def testIndividualAllCanWin2(self):
        challenge = Challenge.objects.create(name="Marathon",
                                             type="INDV",
                                             style="ALL",
                                             distance=135,
                                             startdate=datetime.datetime(2013, 1, 1).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             enddate=datetime.datetime(2013, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             ante=25)

        challenge.approvedActivities.add(self.running)

        challenge.addChallenger(self.elmo)
        challenge.addChallenger(self.count)
        challenge.addChallenger(self.bert)
        challenge.addChallenger(self.ernie)

        Transaction.objects.deposit(self.elmo.account, 25)
        Transaction.objects.deposit(self.count.account, 25)
        Transaction.objects.deposit(self.bert.account, 25)
        Transaction.objects.deposit(self.ernie.account, 25)

        self.assertEqual(100, challenge.account.balance)

        self.assertEqual(0, self.elmo.account.balance)
        self.assertEqual(0, self.count.account.balance)
        self.assertEqual(0, self.bert.account.balance)
        self.assertEqual(0, self.ernie.account.balance)

        challenge.performReconciliation()

        self.assertEqual(0, challenge.account.balance, 2)

        self.assertEqual(0, self.elmo.account.balance)
        self.assertEqual(100, self.count.account.balance)
        self.assertEqual(0, self.bert.account.balance)
        self.assertEqual(0, self.ernie.account.balance)

        self.assertEqual(challenge.numWinners, 1)
        self.assertAlmostEqual(challenge.disbursementAmount, Decimal(100), 2)
        self.assertEqual(challenge.totalDisbursed, 100)


    def testIndividualAllCanWin3(self):
        challenge = Challenge.objects.create(name="Marathon",
                                             type="INDV",
                                             style="ALL",
                                             distance=235,
                                             startdate=datetime.datetime(2013, 1, 1).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             enddate=datetime.datetime(2013, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             ante=25)

        challenge.approvedActivities.add(self.running)

        challenge.addChallenger(self.elmo)
        challenge.addChallenger(self.count)
        challenge.addChallenger(self.bert)
        challenge.addChallenger(self.ernie)

        Transaction.objects.deposit(self.elmo.account, 25)
        Transaction.objects.deposit(self.count.account, 25)
        Transaction.objects.deposit(self.bert.account, 25)
        Transaction.objects.deposit(self.ernie.account, 25)

        self.assertEqual(100, challenge.account.balance)

        self.assertEqual(0, self.elmo.account.balance)
        self.assertEqual(0, self.count.account.balance)
        self.assertEqual(0, self.bert.account.balance)
        self.assertEqual(0, self.ernie.account.balance)

        challenge.performReconciliation()

        self.assertEqual(100, challenge.account.balance, 2)

        self.assertEqual(0, self.elmo.account.balance)
        self.assertEqual(0, self.count.account.balance)
        self.assertEqual(0, self.bert.account.balance)
        self.assertEqual(0, self.ernie.account.balance)

        self.assertEqual(challenge.numWinners, 0)
        self.assertAlmostEqual(challenge.disbursementAmount, Decimal(0), 2)
        self.assertEqual(challenge.totalDisbursed, 0)


    def testIndividualWinnerTakesAll(self):
        challenge = Challenge.objects.create(name="Marathon",
                                             type="INDV",
                                             style="ONE",
                                             distance=100,
                                             startdate=datetime.datetime(2013, 1, 1).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             enddate=datetime.datetime(2013, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             ante=25)

        challenge.approvedActivities.add(self.running)

        challenge.addChallenger(self.elmo)
        challenge.addChallenger(self.count)
        challenge.addChallenger(self.ernie)

        Transaction.objects.deposit(self.elmo.account, 25)
        Transaction.objects.deposit(self.count.account, 25)
        Transaction.objects.deposit(self.ernie.account, 25)

        self.assertEqual(75, challenge.account.balance)

        challenge.performReconciliation()

        self.assertEqual(0, challenge.account.balance)

        self.assertEqual(0, self.elmo.account.balance)
        self.assertEqual(75, self.count.account.balance)
        self.assertEqual(0, self.ernie.account.balance)

        self.assertEqual(challenge.numWinners, 1)
        self.assertAlmostEqual(challenge.disbursementAmount, Decimal(75), 2)
        self.assertEqual(challenge.totalDisbursed, 75)

    def testIndividualWinnerTakesAll2(self):
        challenge = Challenge.objects.create(name="Marathon",
                                             type="INDV",
                                             style="ONE",
                                             distance=180,
                                             startdate=datetime.datetime(2013, 1, 1).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             enddate=datetime.datetime(2013, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             ante=25)

        challenge.approvedActivities.add(self.running)

        challenge.addChallenger(self.elmo)
        challenge.addChallenger(self.count)
        challenge.addChallenger(self.ernie)

        Transaction.objects.deposit(self.elmo.account, 25)
        Transaction.objects.deposit(self.count.account, 25)
        Transaction.objects.deposit(self.ernie.account, 25)

        self.assertEqual(75, challenge.account.balance)

        challenge.performReconciliation()

        self.assertEqual(75, challenge.account.balance)

        self.assertEqual(0, self.elmo.account.balance)
        self.assertEqual(0, self.count.account.balance)
        self.assertEqual(0, self.ernie.account.balance)

        self.assertEqual(challenge.numWinners, 0)
        self.assertAlmostEqual(challenge.disbursementAmount, Decimal(0), 2)
        self.assertEqual(challenge.totalDisbursed, 0)

    def testTeamAllCanWin(self):
        challenge = Challenge.objects.create(name="Marathon",
                                             type="TEAM",
                                             style="ALL",
                                             distance=90,
                                             startdate=datetime.datetime(2013, 1, 1).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             enddate=datetime.datetime(2013, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             ante=25)

        challenge.approvedActivities.add(self.running)

        challenge.addChallenger(self.elmo)
        challenge.addChallenger(self.count)
        challenge.addChallenger(self.bert)
        challenge.addChallenger(self.ernie)

        elmosTeam = Team.objects.startTeam(challenge, self.elmo) #92.5 miles
        countsTeam = Team.objects.startTeam(challenge, self.count) #125 miles

        elmosTeam.addChallenger(self.ernie)
        countsTeam.addChallenger(self.bert)

        Transaction.objects.deposit(self.elmo.account, 25)
        Transaction.objects.deposit(self.count.account, 25)
        Transaction.objects.deposit(self.bert.account, 25)
        Transaction.objects.deposit(self.ernie.account, 25)

        self.assertEqual(100, challenge.account.balance)

        challenge.performReconciliation()

        self.assertEqual(0, challenge.account.balance)

        self.assertEqual(25, self.elmo.account.balance)
        self.assertEqual(25, self.count.account.balance)
        self.assertEqual(25, self.bert.account.balance)
        self.assertEqual(25, self.ernie.account.balance)

        self.assertEqual(challenge.numWinners, 4)
        self.assertAlmostEqual(challenge.disbursementAmount, Decimal(25), 2)
        self.assertEqual(challenge.totalDisbursed, 100)

    def testTeamAllCanWin2(self):
        challenge = Challenge.objects.create(name="Marathon",
                                             type="TEAM",
                                             style="ALL",
                                             distance=110,
                                             startdate=datetime.datetime(2013, 1, 1).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             enddate=datetime.datetime(2013, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             ante=25)

        challenge.approvedActivities.add(self.running)

        challenge.addChallenger(self.elmo)
        challenge.addChallenger(self.count)
        challenge.addChallenger(self.bert)
        challenge.addChallenger(self.ernie)

        elmosTeam = Team.objects.startTeam(challenge, self.elmo) #92.5 miles
        countsTeam = Team.objects.startTeam(challenge, self.count) #125 miles

        elmosTeam.addChallenger(self.ernie)
        countsTeam.addChallenger(self.bert)

        Transaction.objects.deposit(self.elmo.account, 25)
        Transaction.objects.deposit(self.count.account, 25)
        Transaction.objects.deposit(self.bert.account, 25)
        Transaction.objects.deposit(self.ernie.account, 25)

        self.assertEqual(100, challenge.account.balance)

        challenge.performReconciliation()

        self.assertEqual(0, challenge.account.balance)

        self.assertEqual(0, self.elmo.account.balance)
        self.assertEqual(50, self.count.account.balance)
        self.assertEqual(50, self.bert.account.balance)
        self.assertEqual(0, self.ernie.account.balance)

        self.assertEqual(challenge.numWinners, 2)
        self.assertAlmostEqual(challenge.disbursementAmount, Decimal(50), 2)
        self.assertEqual(challenge.totalDisbursed, 100)

    def testTeamAllCanWin3(self):
        challenge = Challenge.objects.create(name="Marathon",
                                             type="TEAM",
                                             style="ALL",
                                             distance=150,
                                             startdate=datetime.datetime(2013, 1, 1).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             enddate=datetime.datetime(2013, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             ante=25)

        challenge.approvedActivities.add(self.running)

        challenge.addChallenger(self.elmo)
        challenge.addChallenger(self.count)
        challenge.addChallenger(self.bert)
        challenge.addChallenger(self.ernie)

        elmosTeam = Team.objects.startTeam(challenge, self.elmo) #92.5 miles
        countsTeam = Team.objects.startTeam(challenge, self.count) #125 miles

        elmosTeam.addChallenger(self.ernie)
        countsTeam.addChallenger(self.bert)

        Transaction.objects.deposit(self.elmo.account, 25)
        Transaction.objects.deposit(self.count.account, 25)
        Transaction.objects.deposit(self.bert.account, 25)
        Transaction.objects.deposit(self.ernie.account, 25)

        self.assertEqual(100, challenge.account.balance)

        challenge.performReconciliation()

        self.assertEqual(100, challenge.account.balance)

        self.assertEqual(0, self.elmo.account.balance)
        self.assertEqual(0, self.count.account.balance)
        self.assertEqual(0, self.bert.account.balance)
        self.assertEqual(0, self.ernie.account.balance)

        self.assertEqual(challenge.numWinners, 0)
        self.assertAlmostEqual(challenge.disbursementAmount, Decimal(0), 2)
        self.assertEqual(challenge.totalDisbursed, 0)

    def testTeamWinnerTakesAll(self):
        challenge = Challenge.objects.create(name="Marathon",
                                             type="TEAM",
                                             style="ONE",
                                             distance=100,
                                             startdate=datetime.datetime(2013, 1, 1).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             enddate=datetime.datetime(2013, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             ante=25)

        challenge.approvedActivities.add(self.running)

        challenge.addChallenger(self.elmo)
        challenge.addChallenger(self.count)
        challenge.addChallenger(self.bert)
        challenge.addChallenger(self.ernie)

        elmosTeam = Team.objects.startTeam(challenge, self.elmo) #92.5 miles
        countsTeam = Team.objects.startTeam(challenge, self.count) #125 miles

        elmosTeam.addChallenger(self.ernie)
        countsTeam.addChallenger(self.bert)

        Transaction.objects.deposit(self.elmo.account, 25)
        Transaction.objects.deposit(self.count.account, 25)
        Transaction.objects.deposit(self.bert.account, 25)
        Transaction.objects.deposit(self.ernie.account, 25)

        self.assertEqual(100, challenge.account.balance)

        challenge.performReconciliation()

        self.assertEqual(0, challenge.account.balance)

        self.assertEqual(0, self.elmo.account.balance)
        self.assertEqual(50, self.count.account.balance)
        self.assertEqual(50, self.bert.account.balance)
        self.assertEqual(0, self.ernie.account.balance)

        self.assertEqual(challenge.numWinners, 2)
        self.assertAlmostEqual(challenge.disbursementAmount, Decimal(50), 2)
        self.assertEqual(challenge.totalDisbursed, 100)

    def testTeamWinnerTakesAll2(self):
        challenge = Challenge.objects.create(name="Marathon",
                                             type="TEAM",
                                             style="ONE",
                                             distance=300,
                                             startdate=datetime.datetime(2013, 1, 1).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             enddate=datetime.datetime(2013, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                             ante=25)

        challenge.approvedActivities.add(self.running)

        challenge.addChallenger(self.elmo)
        challenge.addChallenger(self.count)
        challenge.addChallenger(self.bert)
        challenge.addChallenger(self.ernie)

        elmosTeam = Team.objects.startTeam(challenge, self.elmo) #92.5 miles
        countsTeam = Team.objects.startTeam(challenge, self.count) #125 miles

        elmosTeam.addChallenger(self.ernie)
        countsTeam.addChallenger(self.bert)

        Transaction.objects.deposit(self.elmo.account, 25)
        Transaction.objects.deposit(self.count.account, 25)
        Transaction.objects.deposit(self.bert.account, 25)
        Transaction.objects.deposit(self.ernie.account, 25)

        self.assertEqual(100, challenge.account.balance)

        challenge.performReconciliation()

        self.assertEqual(100, challenge.account.balance)

        self.assertEqual(0, self.elmo.account.balance)
        self.assertEqual(0, self.count.account.balance)
        self.assertEqual(0, self.bert.account.balance)
        self.assertEqual(0, self.ernie.account.balance)

        self.assertEqual(challenge.numWinners, 0)
        self.assertAlmostEqual(challenge.disbursementAmount, Decimal(0), 2)
        self.assertEqual(challenge.totalDisbursed, 0)
