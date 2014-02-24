from fitcompetition import tasks


def persistHealthgraphData(strategy, details, response, user=None, *args, **kwargs):
    if user:
        tasks.syncExternalActivities.delay(user.id)