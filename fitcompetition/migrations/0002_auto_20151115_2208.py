# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitcompetition', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='pace',
            field=models.DecimalField(default=0, help_text=b'In meters per second. ( m/s = 26.8224 / minutes per mile )', max_digits=20, decimal_places=16),
        ),
        migrations.AddField(
            model_name='fitnessactivity',
            name='pace',
            field=models.FloatField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='accountingType',
            field=models.CharField(default=b'distance', max_length=20, choices=[(b'distance', b'Distance'), (b'calories', b'Calories'), (b'duration', b'Duration'), (b'pace', b'Pace')]),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='calories',
            field=models.DecimalField(default=0, help_text=b'In calories. No conversion necessary.', max_digits=20, decimal_places=10),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='distance',
            field=models.DecimalField(default=0, help_text=b'In meters.  ( meters = miles / 0.00062137 )', max_digits=20, decimal_places=10),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='duration',
            field=models.DecimalField(default=0, help_text=b'In seconds. ( seconds = hours * 60 * 60 )', max_digits=20, decimal_places=10),
        ),
    ]
