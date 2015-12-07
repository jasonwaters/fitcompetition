import datetime
import json
import uuid

from django.core import mail
from django.test import Client, TestCase
from fitcompetition import tasks
from fitcompetition.models import FitUser, Challenge, ActivityType, Transaction, FitnessActivity, Team
from fitcompetition.settings import TIME_ZONE
from fitcompetition.templatetags.apptags import toMiles, accounting
import pytz

accountingTypes = (('distance', 'miles'),
                   ('calories', 'calories'),
                   ('duration', ''),
                   ('pace', ''))

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

    def testEmailConfirm(self):
        pass

    def testJoinChallenge(self):
        for accountingType, accountingText in accountingTypes:
            self.challenge = Challenge.objects.create(name="Marathon",
                                                      slug=uuid.uuid4(),
                                                      type="INDV",
                                                      style="ALL",
                                                      distance=100,
                                                      calories=100,
                                                      duration=100,
                                                      pace=1,
                                                      accountingType=accountingType,
                                                      startdate=datetime.datetime(2013, 11, 16).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                                      enddate=datetime.datetime(2014, 2, 14).replace(tzinfo=pytz.timezone(TIME_ZONE)),
                                                      ante=25)

            self.challenge.addChallenger(self.user1)

            self.assertEqual(1, len(mail.outbox), "Joined Challenge Email Failed To Send")
            self.assertEqual('You joined "%s"' % self.challenge.name, mail.outbox[0].subject, "Joined Challenge Email Failed To Send")

            text = "must log %s" % accounting(self.challenge, accountingType, self.user1, True)

            self.assertTrue(text.strip() in mail.outbox[0].alternatives[0][0], 'accounting value and metric not shown')

            mail.outbox = []

            self.challenge.removeChallenger(self.user1, force=True)

            self.assertEqual(0, len(mail.outbox), "No transactional email should be sent when a user withdraws from a challenge.")

            self.challenge.delete()

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
        for accountingType, accountingText in accountingTypes:
            now = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE))
            self.challenge = Challenge.objects.create(name="aaa",
                                                      slug=uuid.uuid4(),
                                                      type="INDV",
                                                      style="ALL",
                                                      distance=100,
                                                      calories=100,
                                                      duration=100,
                                                      pace=1,
                                                      accountingType=accountingType,
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

            self.assertTrue("challenge has begun!" in mail.outbox[0].alternatives[0][0], msg="email body wrong for accountingType=%s" % accountingType)
            self.assertTrue("challenge has begun!" in mail.outbox[1].alternatives[0][0], msg="email body wrong for accountingType=%s" % accountingType)

            self.challenge.delete()

    def testChallengeHalf(self):
        for accountingType, accountingText in accountingTypes:
            now = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE))
            self.challenge = Challenge.objects.create(name="aaa",
                                                      slug=uuid.uuid4(),
                                                      type="INDV",
                                                      style="ALL",
                                                      distance=100,
                                                      calories=100,
                                                      duration=100,
                                                      pace=1,
                                                      accountingType=accountingType,
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
                                           calories=100,
                                           distance=120,
                                           hasGPS=True)

            FitnessActivity.objects.create(user=self.user2,
                                           type=self.running,
                                           uri='blah',
                                           duration=50,
                                           date=now,
                                           calories=25,
                                           distance=25,
                                           photo="meh.jpg")

            mail.outbox = []

            tasks.sendChallengeNotifications()

            self.assertEqual(2, len(mail.outbox), '2 challenge half-over emails should have been sent')

            challengers = self.challenge.getChallengersWithActivities()

            self.assertEqual(challengers[0].id, self.user1.id)
            self.assertEqual(challengers[1].id, self.user2.id)

            self.assertEqual("The challenge is half over!", mail.outbox[0].subject)
            self.assertTrue(accounting(challengers[0].total_accounting, accountingType, self.user1, True) in mail.outbox[0].alternatives[0][0])
            self.assertTrue("dominate the leaderboard" in mail.outbox[0].alternatives[0][0])

            self.assertEqual("The challenge is half over!", mail.outbox[1].subject)
            self.assertTrue(accounting(challengers[1].total_accounting, accountingType, self.user1, True) in mail.outbox[1].alternatives[0][0])
            self.assertTrue("on your way to conquer" in mail.outbox[1].alternatives[0][0])

            self.challenge.delete()
            FitnessActivity.objects.all().delete()

    def testChallengeEnd(self):
        for accountingType, accountingText in accountingTypes:

            now = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE))
            self.challenge = Challenge.objects.create(name="aaa",
                                                      slug=uuid.uuid4(),
                                                      type="INDV",
                                                      style="ALL",
                                                      distance=100,
                                                      calories=100,
                                                      duration=100,
                                                      pace=1,
                                                      accountingType=accountingType,
                                                      startdate=now + datetime.timedelta(days=-20),
                                                      enddate=now + datetime.timedelta(days=-2),
                                                      ante=100)

            self.challenge.approvedActivities.add(self.running)

            self.challenge.addChallenger(self.user1)
            self.challenge.addChallenger(self.user2)

            FitnessActivity.objects.create(user=self.user1,
                                           type=self.running,
                                           uri='blah',
                                           duration=100,
                                           date=now + datetime.timedelta(days=-5),
                                           calories=150,
                                           distance=200,
                                           hasGPS=True)

            FitnessActivity.objects.create(user=self.user2,
                                           type=self.running,
                                           uri='blah',
                                           duration=50,
                                           date=now + datetime.timedelta(days=-5),
                                           calories=10,
                                           distance=10,
                                           photo="bla.jpg")

            mail.outbox = []

            tasks.sendChallengeNotifications()
            self.assertEqual(2, len(mail.outbox), '2 challenge ended emails should have been sent')

            challengers = self.challenge.getChallengersWithActivities()

            self.assertEqual(challengers[0].id, self.user1.id)
            self.assertEqual(challengers[1].id, self.user2.id)

            self.assertEqual("The challenge is over!", mail.outbox[0].subject)
            self.assertTrue(accounting(challengers[0].total_accounting, accountingType, self.user1, True) in mail.outbox[0].alternatives[0][0])
            self.assertTrue("We've credited $200" in mail.outbox[0].alternatives[0][0])

            self.assertEqual("The challenge is over!", mail.outbox[1].subject)
            self.assertTrue(accounting(challengers[1].total_accounting, accountingType, self.user1, True) in mail.outbox[1].alternatives[0][0])
            self.assertTrue("sadly you did not complete the challenge" in mail.outbox[1].alternatives[0][0])

            self.challenge.delete()
            FitnessActivity.objects.all().delete()

    def testTeamChallengeEnd(self):
        for accountingType, accountingText in accountingTypes:
            now = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE))
            self.challenge = Challenge.objects.create(name="aaa",
                                                      slug=uuid.uuid4(),
                                                      type="TEAM",
                                                      style="ONE",
                                                      distance=100,
                                                      calories=100,
                                                      duration=100,
                                                      pace=1,
                                                      accountingType=accountingType,
                                                      startdate=now + datetime.timedelta(days=-20),
                                                      enddate=now + datetime.timedelta(days=-2),
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
                                           duration=1000,
                                           date=now + datetime.timedelta(days=-5),
                                           calories=1000,
                                           distance=1500,
                                           hasGPS=True)

            FitnessActivity.objects.create(user=self.user2,
                                           type=self.running,
                                           uri='blah',
                                           duration=200,
                                           date=now + datetime.timedelta(days=-5),
                                           calories=200,
                                           distance=220,
                                           photo="bleh.jpg")

            FitnessActivity.objects.create(user=self.user3,
                                           type=self.running,
                                           uri='blah',
                                           duration=50,
                                           date=now + datetime.timedelta(days=-5),
                                           calories=50,
                                           distance=25,
                                           photo="omg.png",
                                           hasGPS=True)

            mail.outbox = []

            # user 1 : winner
            # user 2 : loser, but achieved goal
            # user 3 : loser, failed to achieve goal

            tasks.sendChallengeNotifications()
            self.assertEqual(3, len(mail.outbox), '2 challenge ended emails should have been sent')

            self.assertEqual("The challenge is over!", mail.outbox[0].subject)
            self.assertTrue("Congratulations, your team won!" in mail.outbox[0].alternatives[0][0])
            self.assertTrue("We've credited $300" in mail.outbox[0].alternatives[0][0])

            self.assertEqual("The challenge is over!", mail.outbox[1].subject)
            self.assertTrue("It was a valiant effort, but you've been beat." in mail.outbox[1].alternatives[0][0])

            self.assertEqual("The challenge is over!", mail.outbox[2].subject)
            self.assertTrue("It was a valiant effort, but you've been beat." in mail.outbox[2].alternatives[0][0])

            self.challenge.delete()
            Team.objects.all().delete()
            FitnessActivity.objects.all().delete()


