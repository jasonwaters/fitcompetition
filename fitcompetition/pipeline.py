from fitcompetition import tasks


def persistHealthgraphData(strategy, details, response, user=None, *args, **kwargs):
    if user:
        tasks.syncRunkeeperData.delay(user.id)
