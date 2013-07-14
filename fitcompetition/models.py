from datetime import datetime
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import BooleanField
from fitcompetition import RunkeeperService
from fitcompetition.RunkeeperService import RunkeeperException
from fitcompetition.settings import TIME_ZONE
from fitcompetition.util import ListUtil
import pytz
from requests import RequestException
from dateutil import parser


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


class FitUserManager(UserManager):
    pass


class FitUser(AbstractUser):
    runkeeperToken = models.CharField(max_length=255, blank=True, null=True, default=None)
    fullname = models.CharField(max_length=255, blank=True, null=True, default=None)
    gender = models.CharField(max_length=1, blank=True, null=True, default=None)
    profile_url = models.CharField(max_length=255, blank=True, null=True, default=None)
    medium_picture = models.CharField(max_length=255, blank=True, null=True, default=None)
    normal_picture = models.CharField(max_length=255, blank=True, null=True, default=None)

    lastHealthGraphUpdate = models.DateTimeField(blank=True, null=True, default=None)
    objects = FitUserManager()

    def __unicode__(self):
        return self.fullname or "Unnamed User"

    def is_authenticated(self):
        return True

    def syncRunkeeperData(self, activityTypesMap=None):
        if activityTypesMap is None:
            activityTypesMap = ListUtil.mappify(ActivityType.objects.all(), 'name')

        successful = self.syncProfileWithRunkeeper()
        successful = successful and FitnessActivity.objects.pruneActivities(self)
        successful = successful and FitnessActivity.objects.syncActivities(self, activityTypesMap)

        if successful:
            self.lastHealthGraphUpdate = datetime.utcnow().replace(tzinfo=pytz.utc)
            self.save()

    def syncProfileWithRunkeeper(self):
        successful = True
        try:
            profile = RunkeeperService.getUserProfile(self)
            self.medium_picture = profile.get('medium_picture')
            self.normal_picture = profile.get('normal_picture')
            self.gender = profile.get('gender')
            self.profile_url = profile.get('profile')
            self.save()
        except(RunkeeperException, RequestException):
            successful = False

        return successful

    def healthGraphStale(self):
        if self.lastHealthGraphUpdate is None:
            return True

        timeago = datetime.now(tz=pytz.timezone(TIME_ZONE)) + relativedelta(minutes=-20)
        return self.lastHealthGraphUpdate < timeago

class ActivityType(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name


class Challenge(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    distance = models.DecimalField(max_digits=16, decimal_places=2)

    startdate = models.DateTimeField(verbose_name='Start Date')
    enddate = models.DateTimeField(verbose_name='End Date')
    ante = CurrencyField(max_digits=16, decimal_places=2, verbose_name="Ante per player")

    approvedActivities = models.ManyToManyField(ActivityType, verbose_name="Approved Activity Types")
    players = models.ManyToManyField(FitUser, through="Challenger", blank=True, null=True, default=None)
    @property
    def moneyInThePot(self):
        return self.ante * self.players.count()

    @property
    def numPlayers(self):
        return self.players.count()

    @property
    def numDays(self):
        return (self.enddate - self.startdate).days

    @property
    def hasEnded(self):
        return self.enddate < datetime.now(tz=pytz.timezone(TIME_ZONE))

    @property
    def hasStarted(self):
        return self.startdate <= datetime.now(tz=pytz.timezone(TIME_ZONE))

    def __unicode__(self):
        return self.name

    def clean(self):
        if self.startdate > self.enddate:
            raise ValidationError("Start Date must be before End Date")


class Challenger(models.Model):
    fituser = models.ForeignKey(FitUser)
    challenge = models.ForeignKey(Challenge)
    date_joined = models.DateTimeField(verbose_name="Date Joined", blank=True, null=True, default=None)
    hasPaid = models.BooleanField(verbose_name="Has Paid", default=False)

    @property
    def user(self):
        return self.fituser

    class Meta:
        db_table = 'fitcompetition_challenge_players'
        unique_together = (('fituser', 'challenge'))


class FitnessActivityManager(models.Manager):
    def pruneActivities(self, user):
        successful = True
        #delete the activities cached in the database that have been deleted on the health graph
        try:
            changelog = RunkeeperService.getChangeLog(user, modifiedSince=user.lastHealthGraphUpdate)
            deletedActivities = changelog.get('fitness_activities', {}).get('deleted', [])

            for deletedUri in deletedActivities:
                try:
                    activity = FitnessActivity.objects.get(uri=deletedUri)
                    activity.delete()
                except FitnessActivity.DoesNotExist:
                    pass
        except(RunkeeperException, RequestException):
            successful = False

        return successful

    def syncActivities(self, user, activityTypesMap):
        successful = True
        #populate the database with activities from the health graph
        try:
            activities = RunkeeperService.getFitnessActivities(user, modifiedSince=user.lastHealthGraphUpdate)
            for activity in activities:
                type = activityTypesMap.get(activity.get('type'), None)
                dbo, created = FitnessActivity.objects.get_or_create(user=user, type=type, uri=activity.get('uri'))
                dbo.duration = activity.get('duration')
                dbo.date = parser.parse(activity.get('start_time')).replace(tzinfo=pytz.timezone(TIME_ZONE))
                dbo.calories = activity.get('total_calories')
                dbo.distance = activity.get('total_distance')
                dbo.save()
        except (RunkeeperException, RequestException) as e:
            successful = False

        return successful


class FitnessActivity(models.Model):
    user = models.ForeignKey(FitUser)
    type = models.ForeignKey(ActivityType)
    uri = models.CharField(max_length=255)
    duration = models.FloatField(blank=True, null=True, default=0)
    date = models.DateTimeField(blank=True, null=True, default=None)
    calories = models.FloatField(blank=True, null=True, default=0)
    distance = models.FloatField(blank=True, null=True, default=0)

    objects = FitnessActivityManager()