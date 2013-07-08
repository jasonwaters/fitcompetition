from dateutil import parser
from django.core.management.base import  BaseCommand
from fitcompetition import RunkeeperService
from fitcompetition.models import FitUser, FitnessActivity, ActivityType
from fitcompetition.settings import TIME_ZONE
from fitcompetition.util import ListUtil
import pytz


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = FitUser.objects.exclude(runkeeperToken__isnull=True).exclude(runkeeperToken__exact='')
        activityTypes = ListUtil.mappify(ActivityType.objects.all(), 'name')

        for user in users:
            activities = RunkeeperService.getActivities(user)
            for activity in activities:
                type = activityTypes.get(activity.get('type'), None)
                dbo, created = FitnessActivity.objects.get_or_create(user=user, type=type, uri=activity.get('uri'))
                dbo.duration = activity.get('duration')
                dbo.date = parser.parse(activity.get('start_time')).replace(tzinfo=pytz.timezone(TIME_ZONE))
                dbo.calories = activity.get('total_calories')
                dbo.distance = activity.get('total_distance')
                dbo.save()


