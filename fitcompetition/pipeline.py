def persistHealthgraphData(details, user=None, *args, **kwargs):
    if user:
        user.refreshFitnessActivities()