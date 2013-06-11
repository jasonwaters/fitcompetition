import datetime
from django.db import models
import healthgraph

START = "2013-06-08" #datetime.date(2013, 1, 8)
END = "2013-07-06" #datetime.date(2013, 7, 6)


class RunkeeperRecord(models.Model):
    name = models.CharField(max_length=255)
    userID = models.IntegerField()
    code = models.CharField(max_length=255)
    token = models.CharField(max_length=255)

    @property
    def profile(self):
        return self.user.get_profile()

    @property
    def records(self):
        return self.user.get_records()

    @property
    def user(self):
        if not getattr(self, '_user', None):
            self._user = healthgraph.User(session=healthgraph.Session(self.token))
        return self._user

    def ensureActivities(self):
        if not getattr(self, 'activitiesIter', None):
            self.activitiesIter = self.user.get_fitness_activity_iter(date_min=START, date_max=END)
            self.activitiesList = []

            for _ in range(self.activitiesIter.count()):
                activity = self.activitiesIter.next()
                if activity.get('type') in ('Running', 'Walking'):
                    self.activitiesList.append(activity)


    @property
    def activities(self):
        self.ensureActivities()
        return self.activitiesList

    @property
    def totalMiles(self):
        self.ensureActivities()

        total = 0
        for activity in self.activitiesList:
            total += activity.get('total_distance')

        return total
