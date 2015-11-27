from django.test import TestCase
from fitcompetition.models import FitUser, FitnessActivity, ActivityType
import datetime
import pytz


class ModelTests(TestCase):
    def setUp(self):
        self.elmo, created = FitUser.objects.get_or_create(username='user1',
                                                           first_name='Elmo',
                                                           last_name='user',
                                                           email='a@a.net',
                                                           is_staff=False,
                                                           fullname="Elmo")

        self.running, created = ActivityType.objects.get_or_create(name='Running')

    def test_activity_pace_specified(self):
        activity = FitnessActivity.objects.create(user=self.elmo,
                                                  type=self.running,
                                                  uri='blah',
                                                  duration=10,
                                                  date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                                  calories=50,
                                                  distance=50,
                                                  pace=10,
                                                  hasGPS=True)

        activity = FitnessActivity.objects.get(id=activity.id)

        self.assertEqual(5, activity.pace)

    def test_activity_pace_not_specified(self):
        activity = FitnessActivity.objects.create(user=self.elmo,
                                                  type=self.running,
                                                  uri='blah',
                                                  duration=10,
                                                  date=datetime.datetime(2013, 1, 2).replace(tzinfo=pytz.utc),
                                                  calories=50,
                                                  distance=50,
                                                  hasGPS=True)

        activity = FitnessActivity.objects.get(id=activity.id)

        self.assertEqual(5, activity.pace)
