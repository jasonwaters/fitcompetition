from fitcompetition.celery import app
from fitcompetition.models import FitUser


@app.task(ignore_result=True)
def syncRunkeeperData(user_id):
    try:
        user = FitUser.objects.get(id=user_id)
        user.syncRunkeeperData()
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
    pass