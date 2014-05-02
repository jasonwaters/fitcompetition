import datetime
import json
from django.core import mail
from django.test import Client, TestCase
from fitcompetition import tasks
from fitcompetition.models import FitUser, Challenge, ActivityType, Transaction, FitnessActivity, Team
from fitcompetition.settings import TIME_ZONE
from fitcompetition.templatetags.apptags import toMeters
import pytz


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

        self.user3 = FitUser.objects.create(username='chewbacca',
                                            password="pbkdf2_sha256$12000$cqeuHZqWbU2u$vuhnwLgqU6haP5d9D2Qdudld1Jpr4dmc1c52zBx7d90=",
                                            first_name='chewbacca',
                                            last_name='furr',
                                            email='chewy@starwars.net',
                                            is_staff=False,
                                            fullname="Chewy")

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
        response = c.get('/api/account-cash-out', {
            'email': "jake@jones.net",
            'amount': 100
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

    def testTeamChallengeEnd(self):
        now = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE))
        self.challenge = Challenge.objects.create(name="aaa",
                                                  type="TEAM",
                                                  style="ONE",
                                                  distance=100,
                                                  startdate=now + datetime.timedelta(days=-20),
                                                  enddate=now + datetime.timedelta(days=-1),
                                                  ante=100)

        self.challenge.approvedActivities.add(self.running)

        self.challenge.addChallenger(self.user1)
        self.challenge.addChallenger(self.user2)
        self.challenge.addChallenger(self.user3)

        team1 = Team.objects.startTeam(self.challenge, self.user1)
        team2 = Team.objects.startTeam(self.challenge, self.user2)
        team3 = Team.objects.startTeam(self.challenge, self.user3)

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
                                       distance=toMeters(101))

        FitnessActivity.objects.create(user=self.user3,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=now + datetime.timedelta(days=-5),
                                       calories=0,
                                       distance=toMeters(50))

        mail.outbox = []

        #user 1 : winner
        #user 2 : loser, but achieved distance
        #user 3 : loser, failed to achieve distance

        tasks.sendChallengeNotifications()
        self.assertEqual(3, len(mail.outbox), '2 challenge ended emails should have been sent')

        self.assertEqual("The challenge is over!", mail.outbox[0].subject)
        self.assertTrue("Congratulations, your team won!" in mail.outbox[0].alternatives[0][0])
        self.assertTrue("We've credited $300" in mail.outbox[0].alternatives[0][0])

        self.assertEqual("The challenge is over!", mail.outbox[1].subject)
        self.assertTrue("It was a valiant effort, but you've been beat." in mail.outbox[1].alternatives[0][0])

        self.assertEqual("The challenge is over!", mail.outbox[2].subject)
        self.assertTrue("It was a valiant effort, but you've been beat." in mail.outbox[2].alternatives[0][0])