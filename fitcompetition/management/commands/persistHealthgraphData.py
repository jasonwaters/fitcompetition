from optparse import make_option
from django.core.management.base import BaseCommand
from fitcompetition.models import FitUser, ActivityType, FitnessActivity
from fitcompetition.util import ListUtil


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--overwrite',
                    action='store_true',
                    dest='overwrite',
                    default=False,
                    help='Replace all activities with latest data from HealthGraph'),
    )

    def handle(self, *args, **options):
        overwrite = options.get('overwrite', False)
        if overwrite:
            FitnessActivity.objects.all().delete()
            FitUser.objects.all().update(lastHealthGraphUpdate=None)

        users = FitUser.objects.exclude(runkeeperToken__isnull=True).exclude(runkeeperToken__exact='')
        activityTypesMap = ListUtil.mappify(ActivityType.objects.all(), 'name')

        for user in users:
            user.syncRunkeeperData(activityTypesMap=activityTypesMap)
