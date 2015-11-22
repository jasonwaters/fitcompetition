from optparse import make_option
import datetime
from django.core.management import BaseCommand
from fitcompetition.models import Challenge, FitnessActivity
from fitcompetition.settings import TIME_ZONE
import pytz


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--reset',
                    action='store_true',
                    dest='reset',
                    default=False,
                    help='Recalculate pace for all activities'),
    )

    def handle(self, *args, **options):
        recalc_all = options.get('reset', False)

        if recalc_all:
            activities = FitnessActivity.objects.all()
        else:
            activities = FitnessActivity.objects.filter(pace=None)

        for activity in activities:
            try:
                activity.pace = activity.distance / activity.duration
            except Exception as err:
                activity.pace = 0

            activity.save()


