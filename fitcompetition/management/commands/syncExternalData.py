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

        make_option('--service',
                    action='store',
                    type="string",
                    dest='serviceName',
                    default=None,
                    help='Limit to a specific integration. See services.Integration object.'),
    )

    def handle(self, *args, **options):
        overwrite = options.get('reset', False)
        service = options.get('serviceName', None)

        if overwrite:
            if service is not None:
                # FitnessActivity.objects.filter(user__integrationName=service).delete()
                FitUser.objects.filter(integrationName=service).update(lastExternalSyncDate=None)
            else:
                # FitnessActivity.objects.all().delete()
                FitUser.objects.all().update(lastExternalSyncDate=None)

        if service is not None:
            integrations = [service]
        else:
            integrations = None

        tasks.syncExternalDataAllUsers.delay(syncActivities=True,
                                             syncProfile=False,
                                             pruneActivities=False,
                                             integrations=integrations)
