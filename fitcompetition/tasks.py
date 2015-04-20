from datetime import datetime, timedelta
from django.db.models import Q
from django.utils import timezone
from fitcompetition.celery import app
from fitcompetition.email import EmailFactory
from fitcompetition.models import FitUser, Challenge, FitnessActivity
from fitcompetition.services import Integration, StravaService
from fitcompetition.settings import TIME_ZONE
import pytz


@app.task(ignore_result=True)
def syncExternalProfile(user_id):
    try:
        user = FitUser.objects.get(id=user_id)
        user.syncExternalProfile()
    except FitUser.DoesNotExist:
        pass


@app.task(ignore_result=True)
def syncExternalActivities(user_id):
    try:
        user = FitUser.objects.get(id=user_id)
        user.syncExternalActivities()
    except FitUser.DoesNotExist:
        pass


@app.task(ignore_result=True)
def pruneExternalActivities(user_id):
    try:
        user = FitUser.objects.get(id=user_id)
        user.pruneExternalActivities()
    except FitUser.DoesNotExist:
        pass


@app.task(ignore_result=True)
def syncExternalData(user_id, syncActivities=True, syncProfile=False, pruneActivities=False):
    if syncProfile:
        syncExternalProfile.delay(user_id)

    if syncActivities:
        syncExternalActivities.delay(user_id)

    if pruneActivities:
        pruneExternalActivities.delay(user_id)


# hourly
@app.task(ignore_result=True)
def syncExternalDataAllUsers(syncActivities=True, syncProfile=False, pruneActivities=False, integrations=None, nowPlayingOnly=True):
    integrationFilter = Q()

    if integrations is None:
        integrations = Integration.all()

    if Integration.RUNKEEPER in integrations:
        integrationFilter |= Q(runkeeperToken__isnull=False)

    if Integration.STRAVA in integrations:
        integrationFilter |= Q(stravaToken__isnull=False)

    if Integration.MAPMYFITNESS in integrations:
        integrationFilter |= Q(mapmyfitnessToken__isnull=False)

    if nowPlayingOnly:
        now = datetime.now(tz=pytz.utc)
        yesterday = now - timedelta(days=1)
        users = FitUser.objects.filter(integrationFilter,
                                       challenger__challenge__startdate__lte=now,
                                       challenger__challenge__enddate__gte=yesterday).distinct()
    else:
        users = FitUser.objects.filter(integrationFilter)

    for user in users:
        syncExternalData.delay(user.id, syncActivities=syncActivities, syncProfile=syncProfile, pruneActivities=pruneActivities)


# hourly
@app.task(ignore_result=True)
def syncStravaActivityDetails():
    now = timezone.localtime(timezone.now())
    thirtyDaysAgo = now - timedelta(days=30)

    activities = FitnessActivity.objects.filter(user__integrationName=Integration.STRAVA,
                                                calories=0,
                                                date__gte=thirtyDaysAgo).prefetch_related('user')

    for activity in activities:
        id = activity.uri.split('/')[-1]
        json = StravaService(activity.user).getFitnessActivity(id)
        activity.calories = json.get('calories')
        activity.distance = json.get('distance')
        activity.duration = json.get('moving_time')
        activity.save()

# daily
@app.task(ignore_result=True)
def sendChallengeNotifications():
    now = timezone.localtime(timezone.now())
    yesterday = now - timedelta(days=1)

    challenges = Challenge.objects.filter(reconciled=False)
    for challenge in challenges:
        # check challenges started
        if challenge.startdate.astimezone(pytz.timezone(TIME_ZONE)).date() == now.date():
            for user in challenge.challengers:
                EmailFactory().challengeStart(user, challenge)

        # check challenges middle
        elif challenge.middate.astimezone(pytz.timezone(TIME_ZONE)).date() == now.date():
            for user in challenge.getChallengersWithActivities():
                EmailFactory().challengeHalf(user, challenge)

        # check challenged ended
        elif challenge.enddate.astimezone(pytz.timezone(TIME_ZONE)) < yesterday:
            upcomingChallenges = Challenge.objects.upcomingChallenges()
            challenge.performReconciliation()
            achievers = challenge.getAchievers()
            for user in challenge.getChallengersWithActivities():
                EmailFactory().challengeEnd(user, challenge, upcomingChallenges, user in achievers)
