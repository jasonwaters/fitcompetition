from optparse import make_option
from django.core.management.base import BaseCommand
from fitcompetition import tasks
from fitcompetition.models import FitUser, FitnessActivity


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--reset',
                    action='store_true',
                    dest='reset',
                    default=False,
                    help='Replace all activities with latest data from HealthGraph'),
    )

    def handle(self, *args, **options):
        overwrite = options.get('reset', False)
        if overwrite:
            FitnessActivity.objects.all().delete()
            FitUser.objects.all().update(lastExternalSyncDate=None)

        tasks.syncExternalDataAllUsers.delay(syncActivities=True,
                                             syncProfile=True,
                                             pruneActivities=True)
