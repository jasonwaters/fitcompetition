from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
from django.core.management.base import  BaseCommand
from fitcompetition import RunkeeperService
from fitcompetition.RunkeeperService import RunkeeperException
from fitcompetition.models import FitUser, FitnessActivity, ActivityType
from fitcompetition.settings import TIME_ZONE
from fitcompetition.util import ListUtil
import pytz
from requests import RequestException


class Command(BaseCommand):
    def handle(self, *args, **options):
        apiFailed = False

        users = FitUser.objects.exclude(runkeeperToken__isnull=True).exclude(runkeeperToken__exact='')
        activityTypes = ListUtil.mappify(ActivityType.objects.all(), 'name')

        for user in users:
            #delete the activities cached in the database that have been deleted on the health graph
            try:
                changelog = RunkeeperService.getChangeLog(user, modifiedSince=user.lastHealthGraphUpdate)
                deletedActivities = changelog.get('fitness_activities', {}).get('deleted', [])

                for deletedUri in deletedActivities:
                    try:
                        activity = FitnessActivity.objects.get(uri=deletedUri)
                        activity.delete()
                    except FitnessActivity.DoesNotExist:
                        pass
            except(RunkeeperException, RequestException):
                apiFailed = True

            #populate the database with activities from the health graph
            try:
                activities = RunkeeperService.getFitnessActivities(user, modifiedSince=user.lastHealthGraphUpdate)
                for activity in activities:
                    type = activityTypes.get(activity.get('type'), None)
                    dbo, created = FitnessActivity.objects.get_or_create(user=user, type=type, uri=activity.get('uri'))
                    dbo.duration = activity.get('duration')
                    dbo.date = parser.parse(activity.get('start_time')).replace(tzinfo=pytz.timezone(TIME_ZONE))
                    dbo.calories = activity.get('total_calories')
                    dbo.distance = activity.get('total_distance')
                    dbo.save()
            except(RunkeeperException, RequestException):
                apiFailed = True

            if not apiFailed:
                user.lastHealthGraphUpdate = datetime.now(tz=pytz.timezone(TIME_ZONE))
                user.save()