import datetime
from decimal import Decimal

from django.core import mail
from django.test import TestCase
from fitcompetition.models import FitUser, Challenge, ActivityType, Transaction, FitnessActivity, Team
from fitcompetition.settings import TIME_ZONE
import pytz
import uuid

accountingTypes = ('distance', 'calories', 'duration', 'pace')


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
                                       duration=50,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=50,
                                       distance=50,
                                       pace=1,
                                       hasGPS=True)

        FitnessActivity.objects.create(user=self.elmo,
                                       type=self.running,
                                       uri='blah',
                                       duration=70,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=70,
                                       distance=70,
                                       pace=1,
                                       hasGPS=True)

        #does not count since evidence is required
        FitnessActivity.objects.create(user=self.elmo,
                                       type=self.running,
                                       uri='blah',
                                       duration=70,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=70,
                                       distance=70,
                                       pace=1)

        FitnessActivity.objects.create(user=self.count,
                                       type=self.running,
                                       uri='blah',
                                       duration=70,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=70,
                                       distance=105,
                                       hasGPS=True,
                                       pace=1.5)

        FitnessActivity.objects.create(user=self.count,
                                       type=self.running,
                                       uri='blah',
                                       duration=70,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=70,
                                       distance=105,
                                       pace=1.5,
                                       photo="moo.gif")

        FitnessActivity.objects.create(user=self.bert,
                                       type=self.running,
                                       uri='blah',
                                       duration=20,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=20,
                                       distance=20,
                                       pace=1,
                                       hasGPS=True,
                                       photo="ack.png")

        FitnessActivity.objects.create(user=self.bert,
                                       type=self.running,
                                       uri='blah',
                                       duration=90,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=90,
                                       distance=90,
                                       pace=1,
                                       hasGPS=True)

        FitnessActivity.objects.create(user=self.ernie,
                                       type=self.running,
                                       uri='blah',
                                       duration=65,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=65,
                                       distance=32.5,
                                       pace=.5,
                                       photo="meh.jpg")

        #does not count since evidence is required
        FitnessActivity.objects.create(user=self.ernie,
                                       type=self.running,
                                       uri='blah',
                                       duration=65,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=65,
                                       distance=65,
                                       pace=.5)


        #elmo 120 miles
        #count 140 miles
        #bert 110 miles
        #ernie 65 miles

    def testChallengeNotEnded(self):
        for accountingType in accountingTypes:
            Transaction.objects.all().delete()
            now = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE))

            start = now - datetime.timedelta(days=7)
            end = now + datetime.timedelta(days=30)

            challenge = Challenge.objects.create(name="Marathon",
                                                 slug=uuid.uuid4(),
                                                 type="INDV",
                                                 style="ALL",
                                                 distance=100,
                                                 duration=100,
                                                 calories=100,
                                                 pace=1,
                                                 accountingType=accountingType,
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
        for accountingType in accountingTypes:
            Transaction.objects.all().delete()

            challenge = Challenge.objects.create(name="Marathon",
                                                 slug=uuid.uuid4(),
                                                 type="INDV",
                                                 style="ALL",
                                                 distance=100,
                                                 calories=100,
                                                 pace=1,
                                                 duration=100,
                                                 accountingType=accountingType,
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

            self.assertEqual(0, self.elmo.account.balance, msg=accountingType)
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
        for accountingType in accountingTypes:
            Transaction.objects.all().delete()
            challenge = Challenge.objects.create(name="Marathon",
                                                 slug=uuid.uuid4(),
                                                 type="INDV",
                                                 style="ALL",
                                                 distance=135,
                                                 calories=135,
                                                 pace=1.4,
                                                 duration=135,
                                                 accountingType=accountingType,
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
        for accountingType in accountingTypes:
            Transaction.objects.all().delete()
            challenge = Challenge.objects.create(name="Marathon",
                                                 slug=uuid.uuid4(),
                                                 type="INDV",
                                                 style="ALL",
                                                 distance=235,
                                                 calories=235,
                                                 duration=235,
                                                 pace=3,
                                                 accountingType=accountingType,
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
        for accountingType in accountingTypes:
            Transaction.objects.all().delete()
            challenge = Challenge.objects.create(name="Marathon",
                                                 slug=uuid.uuid4(),
                                                 type="INDV",
                                                 style="ONE",
                                                 distance=100,
                                                 calories=100,
                                                 duration=100,
                                                 pace=1,
                                                 accountingType=accountingType,
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
        for accountingType in accountingTypes:
            Transaction.objects.all().delete()
            challenge = Challenge.objects.create(name="Marathon",
                                                 slug=uuid.uuid4(),
                                                 type="INDV",
                                                 style="ONE",
                                                 distance=250,
                                                 calories=250,
                                                 duration=250,
                                                 pace=3,
                                                 accountingType=accountingType,
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
        for accountingType in accountingTypes:
            Transaction.objects.all().delete()
            challenge = Challenge.objects.create(name="Marathon",
                                                 slug=uuid.uuid4(),
                                                 type="TEAM",
                                                 style="ALL",
                                                 distance=70,
                                                 calories=90,
                                                 duration=90,
                                                 pace=0.7,
                                                 accountingType=accountingType,
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
        for accountingType in accountingTypes:
            Transaction.objects.all().delete()
            challenge = Challenge.objects.create(name="Marathon",
                                                 slug=uuid.uuid4(),
                                                 type="TEAM",
                                                 style="ALL",
                                                 distance=110,
                                                 duration=110,
                                                 calories=110,
                                                 pace=1.2,
                                                 accountingType=accountingType,
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
        for accountingType in accountingTypes:
            Transaction.objects.all().delete()
            challenge = Challenge.objects.create(name="Marathon",
                                                 slug=uuid.uuid4(),
                                                 type="TEAM",
                                                 style="ALL",
                                                 distance=170,
                                                 duration=150,
                                                 calories=150,
                                                 pace=3,
                                                 accountingType=accountingType,
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
        for accountingType in accountingTypes:
            Transaction.objects.all().delete()
            challenge = Challenge.objects.create(name="Marathon",
                                                 slug=uuid.uuid4(),
                                                 type="TEAM",
                                                 style="ONE",
                                                 distance=100,
                                                 calories=100,
                                                 duration=100,
                                                 pace=1,
                                                 accountingType=accountingType,
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
        for accountingType in accountingTypes:
            Transaction.objects.all().delete()
            challenge = Challenge.objects.create(name="Marathon",
                                                 slug=uuid.uuid4(),
                                                 type="TEAM",
                                                 style="ONE",
                                                 distance=300,
                                                 calories=300,
                                                 duration=300,
                                                 pace=4,
                                                 accountingType=accountingType,
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