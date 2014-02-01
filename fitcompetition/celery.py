from __future__ import absolute_import
from datetime import timedelta
from celery.schedules import crontab

import os

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitcompetition.settings')

app = Celery('fitcompetition')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
    CELERYBEAT_SCHEDULE={
        "sync-runkeeper-data-hourly": {
            "task": "fitcompetition.tasks.syncRunkeeperDataAllUsers",
            "schedule": crontab(minute=0, hour='*/1')
        },
        "send-challenge-notifications-daily": {
            "task": "fitcompetition.tasks.sendChallengeNotifications",
            "schedule": crontab(minute=0, hour=0)
        }
    }
)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
