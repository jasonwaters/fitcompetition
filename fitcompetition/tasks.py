from django.utils import timezone
from fitcompetition.celery import app
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
            print "%s started" % challenge.name

        #check challenges middle
        if challenge.midwaydate.astimezone(pytz.timezone(TIME_ZONE)).date() == now.date():
            print "%s is half over" % challenge.name

        #check challenged ended
        if challenge.enddate.astimezone(pytz.timezone(TIME_ZONE)).date() == now.date():
            print "%s ended" % challenge.name