from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import BooleanField, Sum, Q, Max
from fitcompetition import RunkeeperService
from fitcompetition.RunkeeperService import RunkeeperException
from fitcompetition.settings import TIME_ZONE
from fitcompetition.templatetags.apptags import toMeters
from fitcompetition.util import ListUtil
from fitcompetition.util.ListUtil import createListFromProperty
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
    phoneNumber = models.CharField(max_length=255, blank=True, null=True, default=None)

    lastHealthGraphUpdate = models.DateTimeField(blank=True, null=True, default=None)
    objects = FitUserManager()

    def __unicode__(self):
        return self.fullname or "Unnamed User"

    @property
    def delinquent(self):
        return self.balance < 0

    @property
    def balance(self):
        result = Transaction.objects.filter(user=self).aggregate(balance=Sum('amount'))
        return ListUtil.attr(result, 'balance', 0)

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

    @property
    def lackingDetail(self):
        if self.email is None or self.email == '':
            return True

        if self.phoneNumber is None or self.phoneNumber == '':
            return True

        return False

    class Meta:
        ordering = ['fullname']


class ActivityType(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name


class ChallengeManager(models.Manager):
    def openChallenges(self, userid):
        now = datetime.now(tz=pytz.timezone(TIME_ZONE))
        return self.exclude(players__id=userid).filter(enddate__gt=now)

    def userChallenges(self, userid):
        activeUserChallenges = []
        completedUserChallenges = []

        allUserChallenges = Challenge.objects.filter(players__id=userid).order_by('-enddate')

        for challenge in allUserChallenges:
            if challenge.hasEnded:
                completedUserChallenges.append(challenge)
            else:
                activeUserChallenges.append(challenge)

        return allUserChallenges, activeUserChallenges, completedUserChallenges


class Challenge(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    distance = models.DecimalField(max_digits=16, decimal_places=2)

    startdate = models.DateTimeField(verbose_name='Start Date')
    enddate = models.DateTimeField(verbose_name='End Date')
    ante = CurrencyField(max_digits=16, decimal_places=2, verbose_name="Ante per player")

    approvedActivities = models.ManyToManyField(ActivityType, verbose_name="Approved Activity Types")
    players = models.ManyToManyField(FitUser, through="Challenger", blank=True, null=True, default=None)

    objects = ChallengeManager()

    @property
    def approvedActivityNames(self):
        return createListFromProperty(self.approvedActivities.all(), 'name')

    @property
    def challengers(self):
        # return FitUser.objects.filter(challenge=self).order_by('fullname')
        #return only users without an outstanding balance
        return FitUser.objects.filter(challenge=self).annotate(account_balance=Sum('transaction__amount', distinct=True)).filter(Q(account_balance__gte=0) | Q(account_balance=None)).order_by('fullname')

    def getAchievedGoal(self, fituser):
        if fituser.delinquent:
            return False

        dateFilter = Q(date__gte=self.startdate) & Q(date__lte=self.enddate)
        typeFilter = Q()

        approvedTypes = self.approvedActivities.all()

        for type in approvedTypes:
            typeFilter |= Q(type=type)

        activityFilter = Q(user=fituser) & dateFilter & typeFilter

        dbo = FitnessActivity.objects.filter(activityFilter).aggregate(total_distance=Sum('distance'))
        return dbo.get('total_distance') >= toMeters(self.distance)

    @property
    def numAchieved(self):
        return len(self.getChallengersWithActivities(achieversOnly=True))

    @property
    def achievedValue(self):
        if self.numAchieved == 0:
            return Decimal(0)
        value = self.moneyInThePot / self.numAchieved
        return value.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    def getChallengersWithActivities(self, achieversOnly=False):
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        approvedTypes = self.approvedActivities.all()

        result = []
        if self.startdate <= now:
            dateFilter = Q(fitnessactivity__date__gte=self.startdate) & Q(fitnessactivity__date__lte=self.enddate)
            typeFilter = Q()

            for type in approvedTypes:
                typeFilter |= Q(fitnessactivity__type=type)

            activitiesFilter = dateFilter & typeFilter

            challengersList = self.challengers
            l = []

            for u in challengersList:
                l.append(u.id)

            if achieversOnly:
                result = FitUser.objects.filter(id__in=l).filter(activitiesFilter).annotate(total_distance=Sum('fitnessactivity__distance', distinct=True), latest_activity_date=Max('fitnessactivity__date')).exclude(total_distance__lt=toMeters(self.distance)).order_by('-total_distance')
            else:
                result = FitUser.objects.filter(id__in=l).filter(activitiesFilter).annotate(total_distance=Sum('fitnessactivity__distance', distinct=True), latest_activity_date=Max('fitnessactivity__date')).order_by('-total_distance')

        return result

    @property
    def moneyInThePot(self):
        return self.ante * self.numPlayers

    @property
    def numPlayers(self):
        return self.challengers.count()

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
                dbo, created = FitnessActivity.objects.get_or_create(user=user, uri=activity.get('uri'))
                dbo.type = type
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
    type = models.ForeignKey(ActivityType, blank=True, null=True, default=None)
    uri = models.CharField(max_length=255)
    duration = models.FloatField(blank=True, null=True, default=0)
    date = models.DateTimeField(blank=True, null=True, default=None)
    calories = models.FloatField(blank=True, null=True, default=0)
    distance = models.FloatField(blank=True, null=True, default=0)

    objects = FitnessActivityManager()


class Transaction(models.Model):
    date = models.DateField(blank=True)
    user = models.ForeignKey(FitUser)
    description = models.CharField(max_length=255)
    amount = CurrencyField(max_digits=16, decimal_places=2)
    challenge = models.ForeignKey(Challenge, blank=True, null=True, default=None)