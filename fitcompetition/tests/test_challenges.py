import datetime
from django.test import TestCase
from fitcompetition.models import Challenge
from fitcompetition.settings import TIME_ZONE
import pytz
import uuid


class ChallengeTests(TestCase):
    def setUp(self):
        self.c1 = Challenge.objects.create(name="aaa",
                                           slug=uuid.uuid4(),
                                           type="INDV",
                                           style="ALL",
                                           distance=100,
                                           startdate=datetime.datetime(2014, 1, 1, tzinfo=pytz.timezone(TIME_ZONE)),
                                           enddate=datetime.datetime(2014, 1, 10, tzinfo=pytz.timezone(TIME_ZONE)),
                                           ante=10)

        self.c2 = Challenge.objects.create(name="bbb",
                                           slug=uuid.uuid4(),
                                           type="INDV",
                                           style="ONE",
                                           distance=100,
                                           startdate=datetime.datetime(2014, 1, 1, tzinfo=pytz.timezone(TIME_ZONE)),
                                           enddate=datetime.datetime(2014, 4, 1, tzinfo=pytz.timezone(TIME_ZONE)),
                                           ante=20)

        self.c3 = Challenge.objects.create(name="ccc",
                                           slug=uuid.uuid4(),
                                           type="TEAM",
                                           style="ALL",
                                           distance=100,
                                           startdate=datetime.datetime(2014, 1, 1, tzinfo=pytz.timezone(TIME_ZONE)),
                                           enddate=datetime.datetime(2014, 1, 7, tzinfo=pytz.timezone(TIME_ZONE)),
                                           ante=30)

        self.c4 = Challenge.objects.create(name="ddd",
                                           slug=uuid.uuid4(),
                                           type="TEAM",
                                           style="ONE",
                                           distance=100,
                                           startdate=datetime.datetime(2014, 2, 1, tzinfo=pytz.timezone(TIME_ZONE)),
                                           enddate=datetime.datetime(2014, 3, 1, tzinfo=pytz.timezone(TIME_ZONE)),
                                           ante=30)

    def testLastPossibleJoinDate(self):
        self.utah = pytz.timezone(TIME_ZONE)

        self.c1 = Challenge.objects.get(id=self.c1.id)
        self.c2 = Challenge.objects.get(id=self.c2.id)
        self.c3 = Challenge.objects.get(id=self.c3.id)
        self.c4 = Challenge.objects.get(id=self.c4.id)

        self.assertEqual(pytz.utc.normalize(self.utah.localize(datetime.datetime(2014, 1, 3, 0, 0, 0)).astimezone(self.utah)),
                         self.c1.lastPossibleJoinDate)

        self.assertEqual(pytz.utc.normalize(self.utah.localize(datetime.datetime(2014, 1, 23, 0, 0, 0)).astimezone(self.utah)),
                         self.c2.lastPossibleJoinDate)

        self.assertEqual(pytz.utc.normalize(self.utah.localize(datetime.datetime(2014, 1, 2, 0, 0, 0)).astimezone(self.utah)),
                         self.c3.lastPossibleJoinDate)

        self.assertEqual(pytz.utc.normalize(self.utah.localize(datetime.datetime(2014, 2, 8, 0, 0, 0)).astimezone(self.utah)),
                         self.c4.lastPossibleJoinDate)

    def testStartDateEndDate(self):
        self.utah = pytz.timezone(TIME_ZONE)

        self.c1 = Challenge.objects.get(id=self.c1.id)
        self.c2 = Challenge.objects.get(id=self.c2.id)
        self.c3 = Challenge.objects.get(id=self.c3.id)
        self.c4 = Challenge.objects.get(id=self.c4.id)

        #challenge 1
        start = self.utah.localize(datetime.datetime(2014, 1, 1, 0, 0, 0))
        end = self.utah.localize(datetime.datetime(2014, 1, 10, 23, 59, 59))

        self.assertEqual(pytz.utc.normalize(start.astimezone(self.utah)), self.c1.startdate)
        self.assertEqual(pytz.utc.normalize(end.astimezone(self.utah)), self.c1.enddate)

        self.c1.performReconciliation()
        self.c1 = Challenge.objects.get(id=self.c1.id)

        self.assertEqual(pytz.utc.normalize(start.astimezone(self.utah)), self.c1.startdate)
        self.assertEqual(pytz.utc.normalize(end.astimezone(self.utah)), self.c1.enddate)

        #challenge 2
        start = self.utah.localize(datetime.datetime(2014, 1, 1, 0, 0, 0))
        end = self.utah.localize(datetime.datetime(2014, 4, 1, 23, 59, 59))

        self.assertEqual(pytz.utc.normalize(start.astimezone(self.utah)), self.c2.startdate)
        self.assertEqual(pytz.utc.normalize(end.astimezone(self.utah)), self.c2.enddate)

        self.c2.performReconciliation()
        self.c2 = Challenge.objects.get(id=self.c2.id)

        self.assertEqual(pytz.utc.normalize(start.astimezone(self.utah)), self.c2.startdate)
        self.assertEqual(pytz.utc.normalize(end.astimezone(self.utah)), self.c2.enddate)

        #challenge 3
        start = self.utah.localize(datetime.datetime(2014, 1, 1, 0, 0, 0))
        end = self.utah.localize(datetime.datetime(2014, 1, 7, 23, 59, 59))

        self.assertEqual(pytz.utc.normalize(start.astimezone(self.utah)), self.c3.startdate)
        self.assertEqual(pytz.utc.normalize(end.astimezone(self.utah)), self.c3.enddate)

        self.c3.performReconciliation()
        self.c3 = Challenge.objects.get(id=self.c3.id)

        self.assertEqual(pytz.utc.normalize(start.astimezone(self.utah)), self.c3.startdate)
        self.assertEqual(pytz.utc.normalize(end.astimezone(self.utah)), self.c3.enddate)

        #challenge 4
        start = self.utah.localize(datetime.datetime(2014, 2, 1, 0, 0, 0))
        end = self.utah.localize(datetime.datetime(2014, 3, 1, 23, 59, 59))

        self.assertEqual(pytz.utc.normalize(start.astimezone(self.utah)), self.c4.startdate)
        self.assertEqual(pytz.utc.normalize(end.astimezone(self.utah)), self.c4.enddate)

        self.c4.performReconciliation()
        self.c4 = Challenge.objects.get(id=self.c4.id)

        self.assertEqual(pytz.utc.normalize(start.astimezone(self.utah)), self.c4.startdate)
        self.assertEqual(pytz.utc.normalize(end.astimezone(self.utah)), self.c4.enddate)

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