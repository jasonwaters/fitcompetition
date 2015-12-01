# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitcompetition', '0005_auto_20151201_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='FitUser',
            name='last_login',
            field=models.DateTimeField(null=True, verbose_name='last login', blank=True)
        )
    ]
