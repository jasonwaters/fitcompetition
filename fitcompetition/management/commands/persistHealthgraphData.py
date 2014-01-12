from optparse import make_option
from django.core.management.base import BaseCommand
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
            FitUser.objects.all().update(lastHealthGraphUpdate=None)

        users = FitUser.objects.exclude(runkeeperToken__isnull=True).exclude(runkeeperToken__exact='')

        for user in users:
            user.syncRunkeeperData()
