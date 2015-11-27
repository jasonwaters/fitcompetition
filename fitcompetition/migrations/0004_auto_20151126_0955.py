# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitcompetition', '0003_auto_20151115_2210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fitnessactivity',
            name='pace',
            field=models.FloatField(default=0),
        ),
    ]
