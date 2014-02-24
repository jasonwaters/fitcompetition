from django.db.models import Q
from django.utils import timezone
from fitcompetition.celery import app
from fitcompetition.email import EmailFactory
from fitcompetition.models import FitUser, Challenge
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


#hourly
@app.task(ignore_result=True)
def syncExternalDataAllUsers(syncActivities=True, syncProfile=False, pruneActivities=False):
    filter = Q()

    filter |= Q(runkeeperToken__isnull=False)
    filter |= Q(mapmyfitnessToken__isnull=False)

    users = FitUser.objects.filter(filter)

    for user in users:
        syncExternalData.delay(user.id, syncActivities=syncActivities, syncProfile=syncProfile, pruneActivities=pruneActivities)


#daily
@app.task(ignore_result=True)
def sendChallengeNotifications():
    now = timezone.localtime(timezone.now())

    challenges = Challenge.objects.filter(reconciled=False)
    for challenge in challenges:
        #check challenges started
        if challenge.startdate.astimezone(pytz.timezone(TIME_ZONE)).date() == now.date():
            for user in challenge.challengers:
                EmailFactory().challengeStart(user, challenge)

        #check challenges middle
        elif challenge.middate.astimezone(pytz.timezone(TIME_ZONE)).date() == now.date():
            for user in challenge.getChallengersWithActivities():
                EmailFactory().challengeHalf(user, challenge)

        #check challenged ended
        elif challenge.enddate.astimezone(pytz.timezone(TIME_ZONE)) < now:
            upcomingChallenges = Challenge.objects.upcomingChallenges()
            challenge.performReconciliation()
            achievers = challenge.getAchievers()
            for user in challenge.getChallengersWithActivities():
                EmailFactory().challengeEnd(user, challenge, upcomingChallenges, user in achievers)
