from datetime import datetime, date
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import BooleanField
import healthgraph


class CurrencyField(models.DecimalField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        try:
            return super(CurrencyField, self).to_python(value).quantize(Decimal("0.01"))
        except AttributeError:
            return None


class UniqueBooleanField(BooleanField):
    def pre_save(self, model_instance, add):
        objects = model_instance.__class__.objects
        # If True then set all others as False
        if getattr(model_instance, self.attname):
            objects.update(**{self.attname: False})
        # If no true object exists that isnt saved model, save as True
        elif not objects.exclude(id=model_instance.id).filter(**{self.attname: True}):
            return True
        return getattr(model_instance, self.attname)

# To use with South
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^fitcompetition\.models\.UniqueBooleanField"])
add_introspection_rules([], ["^fitcompetition\.models\.CurrencyField"])


class Goal(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    distance = models.IntegerField()

    startdate = models.DateTimeField(verbose_name='Start Date')
    enddate = models.DateTimeField(verbose_name='End Date')
    ante = CurrencyField(max_digits=16, decimal_places=2, verbose_name="Ante per player")

    isActive = UniqueBooleanField(verbose_name="Is Active")

    @property
    def numDays(self):
        return (self.enddate - self.startdate).days

    def __unicode__(self):
        return self.name

    def clean(self):
        if self.startdate > self.enddate:
            raise ValidationError("Start Date must be before End Date")



class RunkeeperRecord(models.Model):
    name = models.CharField(max_length=255)
    userID = models.IntegerField()
    code = models.CharField(max_length=255)
    token = models.CharField(max_length=255)

    def __unicode__(self):
        return self.userID

    @property
    def isDead(self):
        return self.settings is None

    @property
    def session(self):
        if not getattr(self, '_session', None):
            self._session = healthgraph.Session(self.token)

        return self._session

    @property
    def profile(self):
        if not getattr(self, '_profile', None):
            self._profile = self.user.get_profile()
        return self._profile

    @property
    def records(self):
        if not getattr(self, '_records', None):
            self._records = self.user.get_records()
        return self._records

    @property
    def settings(self):
        if not getattr(self, '_settings', None):
            self._settings = self.user.get_settings()
        return self._settings

    @property
    def user(self):
        if not getattr(self, '_user', None):
            self._user = healthgraph.User(session=self.session)
        return self._user

    def ensureActivities(self):
        if not getattr(self, 'activitiesIter', None):
            try:
                goal = Goal.objects.get(isActive=True)
                self.activitiesIter = self.user.get_fitness_activity_iter(date_min=goal.startdate.strftime('%Y-%m-%d'), date_max=goal.enddate.strftime('%Y-%m-%d'))
            except Goal.DoesNotExist:
                self.activitiesIter = self.user.get_fitness_activity_iter()

            self.activitiesList = []

            for _ in range(self.activitiesIter.count()):
                activity = self.activitiesIter.next()
                if activity.get('type') in ('Running', 'Walking'):
                    self.activitiesList.append(activity)


    @property
    def activeToday(self):
        today = datetime.now().date()

        for activity in self.activities:
            if (activity.get('start_time').date() - today).days == 0:
                return True

        return False

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
