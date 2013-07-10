from datetime import datetime
from django.core.management.base import  BaseCommand
from fitcompetition.models import FitUser, FitnessActivity, ActivityType
from fitcompetition.settings import TIME_ZONE
from fitcompetition.util import ListUtil
import pytz


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = FitUser.objects.exclude(runkeeperToken__isnull=True).exclude(runkeeperToken__exact='')
        activityTypesMap = ListUtil.mappify(ActivityType.objects.all(), 'name')

        for user in users:
            successful = FitnessActivity.objects.pruneActivities(user)
            successful = successful and FitnessActivity.objects.syncActivities(user, activityTypesMap)

            if successful:
                user.lastHealthGraphUpdate = datetime.now(tz=pytz.timezone(TIME_ZONE))
                user.save()
