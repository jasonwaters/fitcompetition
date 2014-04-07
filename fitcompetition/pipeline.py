from fitcompetition import tasks
from fitcompetition.api import subscribeToMailingList


def post_login_tasks(strategy, uid, user=None, *args, **kwargs):
    if user:
        tasks.syncExternalActivities.delay(user.id)

        if user.email is not None and len(user.email) > 0:
            subscribeToMailingList(user)
