from django.core.management.base import  BaseCommand
from fitcompetition.models import FitUser, ActivityType
from fitcompetition.util import ListUtil


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = FitUser.objects.exclude(runkeeperToken__isnull=True).exclude(runkeeperToken__exact='')
        activityTypesMap = ListUtil.mappify(ActivityType.objects.all(), 'name')

        for user in users:
            user.refreshFitnessActivities(activityTypesMap=activityTypesMap)
