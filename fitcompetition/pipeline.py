def persistHealthgraphData(strategy, details, response, user=None, *args, **kwargs):
    if user:
        user.syncRunkeeperData()