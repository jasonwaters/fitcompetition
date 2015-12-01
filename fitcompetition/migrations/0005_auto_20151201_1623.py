# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitcompetition', '0004_auto_20151126_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='FitUser',
            name='last_login',
            field=models.DateTimeField(null=False, verbose_name='last login', blank=False)
        )
    ]
