from datetime import datetime, timedelta
from decimal import Decimal, ROUND_DOWN
import operator
import uuid
import math
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import BooleanField, Sum, Q, Max, Count
from fitcompetition.services import ExternalIntegrationException, getExternalIntegrationService, Activity, Integration
from fitcompetition.settings import TIME_ZONE, TEAM_MEMBER_MAXIMUM
from fitcompetition.templatetags.apptags import toMeters, toMiles
from fitcompetition.util import ListUtil
from fitcompetition.util.ListUtil import createListFromProperty, attr
import os
import pytz
from requests import RequestException

# noinspection PyUnresolvedReferences
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
    mapmyfitnessToken = models.CharField(max_length=255, blank=True, null=True, default=None)
    mapmyfitnessTokenSecret = models.CharField(max_length=255, blank=True, null=True, default=None)
    stravaToken = models.CharField(max_length=255, blank=True, null=True, default=None)

    fullname = models.CharField(max_length=255, blank=True, null=True, default=None)
    gender = models.CharField(max_length=1, blank=True, null=True, default=None)
    profile_url = models.CharField(max_length=255, blank=True, null=True, default=None)
    medium_picture = models.CharField(max_length=255, blank=True, null=True, default=None)
    normal_picture = models.CharField(max_length=255, blank=True, null=True, default=None)
    phoneNumber = models.CharField(max_length=255, blank=True, null=True, default=None)
    integrationName = models.CharField(verbose_name="Integration", max_length=255, blank=True, null=True, default=None)

    account = models.ForeignKey('Account', blank=True, null=True, default=None)

    lastExternalSyncDate = models.DateTimeField(verbose_name="Last Sync", blank=True, null=True, default=None)
    objects = FitUserManager()

    def __unicode__(self):
        return "%s ( %s )" % (self.fullname or "Unnamed User", self.integrationName)

    @property
    def delinquent(self):
        return self.account.balance < 0

    def getDistance(self, challenge):
        filter = challenge.getActivitiesFilter(generic=True) & Q(user=self)
        result = FitnessActivity.objects.filter(filter).aggregate(Sum('distance'))
        return result.get('distance__sum') if result.get('distance__sum') is not None else 0

    def is_authenticated(self):
        return True

    def syncExternalActivities(self):
        successful = FitnessActivity.objects.syncActivities(self)

        if successful:
            self.lastExternalSyncDate = datetime.now(tz=pytz.utc)
            self.save()

    def pruneExternalActivities(self):
        return FitnessActivity.objects.pruneActivities(self)

    def syncExternalProfile(self):
        successful = True
        try:
            profile = getExternalIntegrationService(self).getUserProfile()
            self.medium_picture = profile.get('medium_picture')
            self.normal_picture = profile.get('normal_picture')
            self.gender = profile.get('gender')
            self.profile_url = profile.get('profile_url')
            self.save()
        except(ExternalIntegrationException, RequestException), e:
            successful = False
            if e.forbidden or e.unauthorized:
                self.stripTokens()

        return successful

    def stripTokens(self):
        self.runkeeperToken = None
        self.mapmyfitnessToken = None
        self.mapmyfitnessTokenSecret = None
        self.stravaToken = None
        self.save()

    def healthGraphStale(self):
        if self.lastExternalSyncDate is None:
            return True

        timeago = datetime.now(tz=pytz.utc) + relativedelta(minutes=-20)
        return self.lastExternalSyncDate < timeago

    @property
    def lackingDetail(self):
        if self.email is None or self.email == '':
            return True

        return False

    class Meta:
        ordering = ['fullname']


class ActivityType(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name


class ChallengeManager(models.Manager):
    def upcomingChallenges(self):
        now = datetime.now(tz=pytz.timezone(TIME_ZONE))
        return self.prefetch_related('approvedActivities', 'players').annotate(num_players=Count('players')).filter(startdate__gt=now).order_by('-startdate', '-num_players')

    def currentChallenges(self):
        now = datetime.now(tz=pytz.timezone(TIME_ZONE))
        return self.prefetch_related('approvedActivities', 'players').annotate(num_players=Count('players')).filter(startdate__lte=now, enddate__gte=now).order_by('startdate', '-num_players')

    def pastChallenges(self, daysAgo=None):
        now = datetime.now(tz=pytz.timezone(TIME_ZONE))
        filters = Q(enddate__lt=now)

        if daysAgo is not None:
            filters &= Q(enddate__gt=now-timedelta(days=daysAgo))

        return self.prefetch_related('approvedActivities', 'players').annotate(num_players=Count('players')).filter(filters).order_by('-startdate')

    def activeChallenges(self, userid=None):
        now = datetime.now(tz=pytz.timezone(TIME_ZONE))
        return self.annotate(num_players=Count('players')).filter(players__id=userid, startdate__lte=now, enddate__gte=now).order_by('-startdate',
                                                                                                                                     '-num_players')

    def userChallenges(self, userid):
        activeUserChallenges = []
        upcomingUserChallenges = []
        completedUserChallenges = []

        if userid is not None:
            allUserChallenges = self.prefetch_related('approvedActivities', 'players').annotate(num_players=Count('players')).filter(players__id=userid).order_by('startdate')

            for challenge in allUserChallenges:
                if challenge.hasEnded:
                    completedUserChallenges.append(challenge)
                elif challenge.hasStarted:
                    activeUserChallenges.append(challenge)
                else:
                    upcomingUserChallenges.append(challenge)

        return activeUserChallenges, upcomingUserChallenges, ListUtil.multikeysort(completedUserChallenges, ['-enddate'], getter=operator.attrgetter)


def getAnnotatedUserListWithActivityData(challenge, challengers, activitiesFilter):
    now = datetime.now(tz=pytz.utc)

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
    ('INDV', 'Individual - Each player is on their own to complete the challenge within the time period.'),
    ('TEAM', 'Team - Players team up and their miles are pooled together to reach the goal.'),
)

CHALLENGE_STYLES = (
    ('ALL', 'All Can Win - Every player or team that completes the challenge shares the pot evenly at the end.'),
    ('ONE', 'Winner Takes All - The individual or team at the top of the leaderboard wins the pot.'),
)


class Challenge(models.Model):
    name = models.CharField(max_length=256)
    type = models.CharField(max_length=6, choices=CHALLENGE_TYPES, default='INDV')
    style = models.CharField(max_length=6, choices=CHALLENGE_STYLES, default='ALL')
    description = models.TextField(blank=True)
    distance = models.DecimalField(max_digits=16, decimal_places=2)

    startdate = models.DateTimeField(verbose_name='Start Date')
    middate = models.DateTimeField(verbose_name='Mid Date', blank=True, null=True, default=None)
    enddate = models.DateTimeField(verbose_name='End Date')
    ante = CurrencyField(max_digits=16, decimal_places=2, verbose_name="Ante per player")

    approvedActivities = models.ManyToManyField(ActivityType, verbose_name="Approved Activity Types")
    players = models.ManyToManyField(FitUser, through="Challenger", blank=True, null=True, default=None)

    reconciled = models.BooleanField(default=False)
    disbursementAmount = CurrencyField(max_digits=16, decimal_places=2, blank=True, null=True, default=0)
    numWinners = models.IntegerField(blank=True, null=True, default=0)
    totalDisbursed = CurrencyField(max_digits=16, decimal_places=2, blank=True, null=True, default=0)

    account = models.ForeignKey('Account', blank=True, null=True, default=None)

    objects = ChallengeManager()

    @property
    def isTypeIndividual(self):
        return self.type == 'INDV'

    @property
    def isTypeTeam(self):
        return self.type == 'TEAM'

    @property
    def isStyleAllCanWin(self):
        return self.style == 'ALL'

    @property
    def isStyleWinnerTakesAll(self):
        return self.style == 'ONE'

    def performReconciliation(self):
        if self.reconciled or not self.hasEnded:
            return

        achievers = self.getAchievers()

        dollars = (self.moneyInThePot / max(1, len(achievers))).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

        for user in achievers:
            Transaction.objects.transact(self.account,
                                         user.account,
                                         dollars,
                                         'Disbursement to %s' % user.fullname,
                                         'Disbursement for "%s"' % self.name)

        self.numWinners = len(achievers)
        self.disbursementAmount = dollars if self.numWinners > 0 else 0
        self.totalDisbursed = self.disbursementAmount * self.numWinners

        self.reconciled = True
        self.save()

    @property
    def approvedActivityNames(self):
        return createListFromProperty(self.approvedActivities.all(), 'name')

    @property
    def challengers(self):
        return self.players.order_by('fullname')

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
    def rankedTeams(self):
        teams = self.teams.filter(challenge=self).select_related('captain').prefetch_related('members').annotate(num_members=Count('members'))
        return ListUtil.multikeysort(teams, ['-averageDistance'], getter=operator.attrgetter)

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

    def getAchievers(self):
        if self.isTypeIndividual:
            winners = self.players.filter(self.getActivitiesFilter()).annotate(total_distance=Sum('fitnessactivity__distance', distinct=True),
                                                                                   latest_activity_date=Max('fitnessactivity__date')).exclude(total_distance__lt=toMeters(self.distance))

            if self.isStyleWinnerTakesAll:
                return winners[:1]
            elif self.isStyleAllCanWin:
                return winners
        elif self.isTypeTeam:
            teams = self.rankedTeams

            if self.isStyleWinnerTakesAll:
                try:
                    topTeam = list(teams[:1])[0]
                    if toMiles(topTeam.averageDistance) > self.distance:
                        return topTeam.members.all()
                except IndexError:
                    #if there are no teams for the challenge
                    pass

                return list()
            elif self.isStyleAllCanWin:
                winners = list()
                for team in teams:
                    if toMiles(team.averageDistance) > self.distance:
                        winners += list(team.members.all())

                return winners

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

    def getRecentActivities(self):
        now = datetime.now(tz=pytz.timezone(TIME_ZONE))
        yesterday = now + relativedelta(hours=-24)

        filter = self.getActivitiesFilter(generic=True)
        filter = filter & Q(date__gt=yesterday) & Q(user__in=self.players.all())

        return FitnessActivity.objects.filter(filter).select_related('type', 'user').order_by('-date')

    def getChallengersWithActivities(self):
        return getAnnotatedUserListWithActivityData(self, self.players.all(), self.getActivitiesFilter())

    @property
    def moneyInThePot(self):
        return self.ante * self.numPlayers

    @property
    def numPlayers(self):
        np = attr(self, 'num_players', None)
        if np is not None:
            return np
        else:
            return self.players.count()

    @property
    def numDays(self):
        #we add 1 because we include the end date in the calculation
        return (self.enddate - self.startdate).days + 1

    @property
    def hasEnded(self):
        return self.enddate < datetime.now(tz=pytz.utc)

    @property
    def hasStarted(self):
        return self.startdate <= datetime.now(tz=pytz.utc)

    @property
    def lastPossibleJoinDate(self):
        dropDeadDays = self.numDays / 4
        return self.startdate + timedelta(days=dropDeadDays)

    @property
    def canJoin(self):
        return datetime.now(tz=pytz.utc).date() <= self.lastPossibleJoinDate.date()

    def __unicode__(self):
        return self.name

    def clean(self):
        if self.startdate > self.enddate:
            raise ValidationError("Start Date must be before End Date")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        startdate = pytz.timezone(TIME_ZONE).normalize(self.startdate)
        enddate = pytz.timezone(TIME_ZONE).normalize(self.enddate)

        self.startdate = startdate.replace(hour=0, minute=0, second=0)
        self.enddate = enddate.replace(hour=23, minute=59, second=59)

        self.middate = self.startdate + ((self.enddate - self.startdate) / 2)

        super(Challenge, self).save(force_insert, force_update, using, update_fields)


class TeamManager(models.Manager):
    def withdrawAll(self, challenge, user, except_for=None):
        teams = self.filter(challenge=challenge).exclude(id=except_for.id) if except_for is not None else self.filter(challenge_id=challenge)

        for team in teams:
            team.members.remove(user)

        if except_for is not None:
            except_for.members.add(user)

        Team.objects.filter(captain=user).annotate(num_members=Count('members')).filter(num_members=0).delete()

    def startTeam(self, challenge, user):
        self.withdrawAll(challenge, user)

        team, created = self.get_or_create(challenge=challenge, captain=user)
        team.name = "%s's Team" % user.first_name
        team.members.add(user)
        team.save()

        return team


class Team(models.Model):
    name = models.CharField(max_length=256)
    challenge = models.ForeignKey(Challenge, related_name="teams")
    members = models.ManyToManyField(FitUser, blank=True, null=True, default=None, related_name='members')
    captain = models.ForeignKey(FitUser, blank=True, null=True, default=None, related_name='captain')

    objects = TeamManager()

    def __init__(self, *args, **kwargs):
        self._distanceCache = None
        super(Team, self).__init__(*args, **kwargs)

    def getMembersWithActivities(self):
        return getAnnotatedUserListWithActivityData(self.challenge,
                                                    self.members.all(),
                                                    self.challenge.getActivitiesFilter())

    def addChallenger(self, user):
        if self.members.count() < TEAM_MEMBER_MAXIMUM:
            Team.objects.withdrawAll(self.challenge, user, except_for=self)

    def removeChallenger(self, user):
        self.members.remove(user)

    @property
    def distance(self):
        if self._distanceCache is None:
            filter = self.challenge.getActivitiesFilter(generic=True)

            userFilter = Q()

            for member in self.members.all():
                userFilter |= Q(user=member)

            filter = filter & userFilter
            #TODO: Fix this N+1 Select
            result = FitnessActivity.objects.filter(filter).aggregate(Sum('distance'))
            self._distanceCache = result.get('distance__sum') if result.get('distance__sum') is not None else 0

        return self._distanceCache


    @property
    def averageDistance(self):
        num_players = attr(self, 'num_members') if attr(self, 'num_members') is not None else self.members.count()
        return self.distance / max(num_players, 1)

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
        thirtyDaysAgo = datetime.now(tz=pytz.utc) + timedelta(days=-30)
        service = getExternalIntegrationService(user)

        try:
            if user.integrationName == Integration.RUNKEEPER:
                #delete the activities cached in the database that have been deleted on the health graph
                changelog = service.getChangeLog(modifiedNoEarlierThan=thirtyDaysAgo)
                deletedActivities = changelog.get('fitness_activities', {}).get('deleted', [])

                for deletedUri in deletedActivities:
                    try:
                        activity = self.get(uri=deletedUri)
                        activity.delete()
                    except FitnessActivity.DoesNotExist:
                        pass
            elif user.integrationName == Integration.MAPMYFITNESS:
                apiActivities = service.getFitnessActivities(noEarlierThan=thirtyDaysAgo)
                dbActivities = self.filter(user=user, date__gt=thirtyDaysAgo)

                if len(apiActivities) != len(dbActivities):
                    uris = {}
                    for apiActivity in apiActivities:
                        uri = apiActivity.get('_links').get('self')[0].get('href')
                        uris[uri] = True

                    for dbActivity in dbActivities:
                        if not uris.get(dbActivity.uri, False):
                            #it was deleted from mapmyfitness
                            dbActivity.delete()

        except(ExternalIntegrationException, RequestException), e:
            successful = False
            if e.forbidden or e.unauthorized:
                user.stripTokens()

        return successful

    def syncActivities(self, user):
        successful = True
        #populate the database with activities from the health graph
        try:
            next = {'hasMore': True, 'url': None}

            while next.get('hasMore'):
                activities, next = getExternalIntegrationService(user).getFitnessActivities(modifiedSince=user.lastExternalSyncDate, url=next.get('url'))

                for activity in activities:
                    activity = Activity(activity, user.integrationName)

                    type, created = ActivityType.objects.get_or_create(name=activity.get('type'))

                    if activity.get('distance') is not None and activity.get('distance') > 0:
                        dbo, created = FitnessActivity.objects.get_or_create(user=user, uri=activity.get('uri'))
                        dbo.type = type
                        dbo.duration = activity.get('duration')
                        dbo.date = activity.get('date')
                        dbo.calories = activity.get('calories')
                        dbo.distance = activity.get('distance')
                        dbo.hasGPS = activity.get('hasGPS')
                        dbo.save()

        except (ExternalIntegrationException, RequestException), e:
            successful = False
            if e.forbidden or e.unauthorized:
                user.stripTokens()

        return successful


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('activity_images', filename)


class FitnessActivity(models.Model):
    user = models.ForeignKey(FitUser)
    type = models.ForeignKey(ActivityType, blank=True, null=True, default=None)
    uri = models.CharField(max_length=255)
    duration = models.FloatField(blank=True, null=True, default=0)
    date = models.DateTimeField(blank=True, null=True, default=None)
    calories = models.FloatField(blank=True, null=True, default=0)
    distance = models.FloatField(blank=True, null=True, default=0)
    photo = models.ImageField(upload_to=get_file_path, default=None, null=True)
    hasGPS = models.BooleanField(default=False)

    objects = FitnessActivityManager()


class Account(models.Model):
    description = models.CharField(max_length=255)

    @property
    def balance(self):
        result = Transaction.objects.filter(account=self).aggregate(balance=Sum('amount'))
        return ListUtil.attr(result, 'balance', 0.0)

    def __unicode__(self):
        return "%s ( $%s )" % (self.description, self.balance)


class TransactionManager(models.Manager):
    def transact(self, fromAccount, toAccount, amount, fromMemo, toMemo):
        now = datetime.now(tz=pytz.timezone(TIME_ZONE))

        self.create(date=now,
                    account=fromAccount,
                    description=fromMemo,
                    amount=amount * -1)

        self.create(date=now,
                    account=toAccount,
                    description=toMemo,
                    amount=amount)

    def deposit(self, account, amount):
        now = datetime.now(tz=pytz.timezone(TIME_ZONE))

        self.create(date=now,
                    account=account,
                    description="Deposit",
                    amount=amount,
                    isCashflow=True)

    def withdraw(self, account, amount):
        now = datetime.now(tz=pytz.timezone(TIME_ZONE))

        self.create(date=now,
                    account=account,
                    description="Withdrawal",
                    amount=math.fabs(amount) * -1,
                    isCashflow=True)


class Transaction(models.Model):
    date = models.DateField(blank=True)
    account = models.ForeignKey(Account)
    description = models.CharField(max_length=255)
    amount = CurrencyField(max_digits=16, decimal_places=2)
    isCashflow = models.BooleanField(verbose_name="Is Cashflow In/Out", default=False)

    objects = TransactionManager()
