from django.utils import timezone
from fitcompetition.celery import app
from fitcompetition.email import EmailFactory
from fitcompetition.models import FitUser, Challenge
from fitcompetition.settings import TIME_ZONE
import pytz


@app.task(ignore_result=True)
def syncRunkeeperData(user_id, syncProfile=True):
    try:
        user = FitUser.objects.get(id=user_id)
        user.syncRunkeeperData(syncProfile=syncProfile)
    except FitUser.DoesNotExist:
        pass

#hourly
@app.task(ignore_result=True)
def syncRunkeeperDataAllUsers():
    users = FitUser.objects.exclude(runkeeperToken__isnull=True).exclude(runkeeperToken__exact='')

    for user in users:
        syncRunkeeperData.delay(user.id)


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
            challenge.performReconciliation()
            for user in challenge.getChallengersWithActivities():
                EmailFactory().challengeEnd(user, challenge)
