from datetime import datetime
from decimal import Decimal, ROUND_DOWN
import operator
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import BooleanField, Sum, Q, Max, Count
from fitcompetition import RunkeeperService
from fitcompetition.RunkeeperService import RunkeeperException
from fitcompetition.settings import TIME_ZONE
from fitcompetition.templatetags.apptags import toMeters
from fitcompetition.util import ListUtil
from fitcompetition.util.ListUtil import createListFromProperty, attr
import pytz
from requests import RequestException
from dateutil import parser
import signals


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
    def account(self):
        try:
            return Account.objects.get(user=self)
        except Account.DoesNotExist:
            return None

    @property
    def delinquent(self):
        return self.balance < 0

    def getDistance(self, challenge):
        filter = challenge.getActivitiesFilter(generic=True) & Q(user=self)
        result = FitnessActivity.objects.filter(filter).aggregate(Sum('distance'))
        return result.get('distance__sum') if result.get('distance__sum') is not None else 0

    @property
    def balance(self):
        result = Transaction.objects.filter(user=self).aggregate(balance=Sum('amount'))
        return ListUtil.attr(result, 'balance', 0)

    def is_authenticated(self):
        return True

    def syncRunkeeperData(self, activityTypesMap=None, syncProfile=True):
        if activityTypesMap is None:
            activityTypesMap = ListUtil.mappify(ActivityType.objects.all(), 'name')

        successful = self.syncProfileWithRunkeeper() if syncProfile else True
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
        if userid is not None:
            return self.annotate(num_players=Count('players')).exclude(players__id=userid).filter(enddate__gt=now).order_by('-num_players')
        else:
            return self.annotate(num_players=Count('players')).filter(enddate__gt=now).order_by('-num_players')

    def pastChallenges(self):
        now = datetime.now(tz=pytz.timezone(TIME_ZONE))
        return self.annotate(num_players=Count('players')).filter(enddate__lt=now).order_by('-startdate')

    def userChallenges(self, userid):
        allUserChallenges = []
        activeUserChallenges = []
        completedUserChallenges = []

        if userid is not None:
            allUserChallenges = self.annotate(num_players=Count('players')).filter(players__id=userid).order_by('-enddate')

            for challenge in allUserChallenges:
                if challenge.hasEnded:
                    completedUserChallenges.append(challenge)
                else:
                    activeUserChallenges.append(challenge)

        return allUserChallenges, ListUtil.multikeysort(activeUserChallenges, ['startdate'], getter=operator.attrgetter), completedUserChallenges


def getAnnotatedUserListWithActivityData(challenge, challengers, activitiesFilter):
    now = datetime.utcnow().replace(tzinfo=pytz.utc)

    users_with_activities = []
    activitySet = set()

    if challenge.startdate <= now:
        users_with_activities = challengers.filter(activitiesFilter).annotate(
            total_distance=Sum('fitnessactivity__distance', distinct=True),
            latest_activity_date=Max('fitnessactivity__date')).order_by('-total_distance')

        activitySet = set(user.id for user in users_with_activities)

        users_with_activities = list(users_with_activities)

    users_with_no_activities = filter(lambda x: x.id not in activitySet, challengers)
    users = users_with_activities + users_with_no_activities

    return users


CHALLENGE_TYPES = (
    ('SIMP', 'Simple - Complete the challenge and get paid.'),
    ('WINR', 'Winner Takes All - First place takes the pot.'),
    ('TEAM', 'Teams - The pot is shared between members of the winning team.')
)


class Challenge(models.Model):
    name = models.CharField(max_length=256)
    type = models.CharField(max_length=6, choices=CHALLENGE_TYPES, default='SIMP')
    description = models.TextField(blank=True)
    distance = models.DecimalField(max_digits=16, decimal_places=2)

    startdate = models.DateTimeField(verbose_name='Start Date')
    enddate = models.DateTimeField(verbose_name='End Date')
    ante = CurrencyField(max_digits=16, decimal_places=2, verbose_name="Ante per player")

    approvedActivities = models.ManyToManyField(ActivityType, verbose_name="Approved Activity Types")
    players = models.ManyToManyField(FitUser, through="Challenger", blank=True, null=True, default=None)

    objects = ChallengeManager()

    @property
    def account(self):
        try:
            return Account.objects.get(challenge=self)
        except Account.DoesNotExist:
            return None

    @property
    def isTypeSimple(self):
        return self.type == 'SIMP'

    @property
    def isTypeWinnerTakesAll(self):
        return self.type == 'WINR'

    @property
    def isTypeTeam(self):
        return self.type == 'TEAM'

    @property
    def approvedActivityNames(self):
        return createListFromProperty(self.approvedActivities.all(), 'name')

    @property
    def challengers(self):
        return FitUser.objects.filter(challenge=self).order_by('fullname')

    def addChallenger(self, user):
        try:
            self.challenger_set.get(fituser=user)
        except Challenger.DoesNotExist:
            now = datetime.now(tz=pytz.timezone(TIME_ZONE))
            Challenger.objects.create(challenge=self,
                                      fituser=user,
                                      date_joined=now)

    def removeChallenger(self, user, force=False):
        try:
            challenger = Challenger.objects.get(challenge=self, fituser=user)
            if not self.hasStarted or force:
                challenger.delete()
        except Challenger.DoesNotExist:
            return False


    @property
    def teams(self):
        return Team.objects.filter(challenge=self).order_by('name')

    def getAchievedGoal(self, fituser):
        if not fituser.is_authenticated():
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
        return self.challengers.filter(self.getActivitiesFilter()).annotate(
            total_distance=Sum('fitnessactivity__distance', distinct=True),
            latest_activity_date=Max('fitnessactivity__date')).exclude(total_distance__lt=toMeters(self.distance)).count()

    @property
    def achievedValue(self):
        if self.numAchieved == 0:
            return Decimal(0)
        value = self.moneyInThePot / self.numAchieved
        return value.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    def getActivitiesFilter(self, generic=False):
        def fieldName(name):
            if generic:
                return name
            else:
                return 'fitnessactivity__%s' % name

        approvedTypes = self.approvedActivities.all()

        dateFilter = Q(**{fieldName('date__gte'): self.startdate})
        dateFilter = dateFilter & Q(**{fieldName('date__lte'): self.enddate})
        typeFilter = Q()

        for type in approvedTypes:
            typeFilter |= Q(**{fieldName('type'): type})

        return dateFilter & typeFilter

    def getChallengersWithActivities(self):
        return getAnnotatedUserListWithActivityData(self, self.challengers, self.getActivitiesFilter())

    @property
    def moneyInThePot(self):
        return self.ante * self.numPlayers

    @property
    def numPlayers(self):
        np = attr(self, 'num_players', None)
        if np is not None:
            return np
        else:
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


class TeamManager(models.Manager):
    def withdrawAll(self, challenge_id, user, except_for=None):
        teams = self.filter(challenge_id=challenge_id).exclude(id=except_for.id) if except_for is not None else self.filter(challenge_id=challenge_id)

        for team in teams:
            team.members.remove(user)

        if except_for is not None:
            except_for.members.add(user)

        Team.objects.filter(captain=user).annotate(num_members=Count('members')).filter(num_members=0).delete()


class Team(models.Model):
    name = models.CharField(max_length=256)
    challenge = models.ForeignKey(Challenge)
    members = models.ManyToManyField(FitUser, blank=True, null=True, default=None, related_name='members')
    captain = models.ForeignKey(FitUser, blank=True, null=True, default=None, related_name='captain')

    objects = TeamManager()

    def getMembersWithActivities(self):
        return getAnnotatedUserListWithActivityData(self.challenge,
                                                    self.members.all(),
                                                    self.challenge.getActivitiesFilter())

    @property
    def distance(self):
        filter = self.challenge.getActivitiesFilter(generic=True)

        userFilter = Q()

        for member in self.members.all():
            userFilter |= Q(user=member)

        filter = filter & userFilter

        result = FitnessActivity.objects.filter(filter).aggregate(Sum('distance'))
        return result.get('distance__sum') if result.get('distance__sum') is not None else 0

    @property
    def averageDistance(self):
        num_players = max(self.members.count(), 1)
        return self.distance / num_players

    def __unicode__(self):
        return self.name


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


class Account(models.Model):
    description = models.CharField(max_length=255)
    user = models.ForeignKey(FitUser, blank=True, null=True, default=None)
    challenge = models.ForeignKey(Challenge, blank=True, null=True, default=None)

    @property
    def balance(self):
        result = Transaction.objects.filter(account=self).aggregate(balance=Sum('amount'))
        return ListUtil.attr(result, 'balance', 0.0)


class Transaction(models.Model):
    date = models.DateField(blank=True)
    account = models.ForeignKey(Account)
    description = models.CharField(max_length=255)
    amount = CurrencyField(max_digits=16, decimal_places=2)
