import datetime
from decimal import Decimal
from django.core import mail
from django.test import TestCase
from fitcompetition.models import FitUser, Challenge, ActivityType, Transaction, FitnessActivity, Team
from fitcompetition.settings import TIME_ZONE
from fitcompetition.templatetags.apptags import toMeters
import pytz


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
                                       distance=toMeters(50),
                                       hasGPS=True)

        FitnessActivity.objects.create(user=self.elmo,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(70),
                                       hasGPS=True)

        #does not count since evidence is required
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
                                       distance=toMeters(70),
                                       hasGPS=True)

        FitnessActivity.objects.create(user=self.count,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(70),
                                       photo="moo.gif")

        FitnessActivity.objects.create(user=self.bert,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(20),
                                       hasGPS=True,
                                       photo="ack.png")

        FitnessActivity.objects.create(user=self.bert,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(90),
                                       hasGPS=True)

        FitnessActivity.objects.create(user=self.ernie,
                                       type=self.running,
                                       uri='blah',
                                       duration=100,
                                       date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                       calories=0,
                                       distance=toMeters(65),
                                       photo="meh.jpg")

        #does not count since evidence is required
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