import datetime
from django.core.management import BaseCommand
from fitcompetition.models import Challenge
from fitcompetition.settings import TIME_ZONE
import pytz


class Command(BaseCommand):
    def handle(self, *args, **options):
        now = datetime.datetime.now(tz=pytz.timezone(TIME_ZONE))

        challenges = Challenge.objects.filter(enddate__lt=now, reconciled=False)

        for challenge in challenges:
            challenge.performReconciliation()


