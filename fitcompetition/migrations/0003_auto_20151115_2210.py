# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def calculate_pace(apps, schema_editor):
    FitnessActivity = apps.get_model("fitcompetition", "FitnessActivity")

    for activity in FitnessActivity.objects.all():
        try:
            activity.pace = activity.distance / activity.duration
        except (TypeError, ZeroDivisionError) as err:
            activity.pace = 0

        activity.save()


class Migration(migrations.Migration):

    dependencies = [
        ('fitcompetition', '0002_auto_20151115_2208'),
    ]

    operations = [
        migrations.RunPython(calculate_pace),
    ]
