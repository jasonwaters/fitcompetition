# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import fitcompetition.models
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='FitUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('runkeeperToken', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('mapmyfitnessToken', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('mapmyfitnessTokenSecret', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('stravaToken', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('fullname', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('gender', models.CharField(default=None, max_length=1, null=True, blank=True)),
                ('profile_url', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('medium_picture', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('normal_picture', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('phoneNumber', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('integrationName', models.CharField(default=None, max_length=255, null=True, verbose_name=b'Integration', blank=True)),
                ('timezone', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('distanceUnit', models.CharField(default=b'mi', max_length=6, choices=[(b'mi', b'Mile'), (b'km', b'Kilometer')])),
                ('lastExternalSyncDate', models.DateTimeField(default=None, null=True, verbose_name=b'Last Sync', blank=True)),
            ],
            options={
                'ordering': ['fullname'],
            },
            managers=[
                ('objects', fitcompetition.models.FitUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255)),
                ('stripeCustomerID', models.CharField(default=None, max_length=255, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ActivityType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('slug', models.SlugField(help_text=b'A slug is a short label for something, containing only letters, numbers, underscores or hyphens.  This unique string is used in the URL.', unique=True, max_length=150, verbose_name=b'Slug')),
                ('private', models.BooleanField(default=False)),
                ('type', models.CharField(default=b'INDV', max_length=6, choices=[(b'INDV', b'Individual - Each player is on their own to complete the challenge within the time period.'), (b'TEAM', b'Team - Players team up and their miles are pooled together to reach the goal.')])),
                ('style', models.CharField(default=b'ALL', max_length=6, choices=[(b'ALL', b'All Can Win - Every player or team that completes the challenge shares the pot evenly at the end.'), (b'ONE', b'Winner Takes All - The individual or team at the top of the leaderboard wins the pot.')])),
                ('description', models.TextField(blank=True)),
                ('accountingType', models.CharField(default=b'distance', max_length=20, choices=[(b'distance', b'Distance'), (b'calories', b'Calories'), (b'duration', b'Duration')])),
                ('distance', models.DecimalField(default=0, max_digits=20, decimal_places=10)),
                ('calories', models.DecimalField(default=0, max_digits=20, decimal_places=10)),
                ('duration', models.DecimalField(default=0, max_digits=20, decimal_places=10)),
                ('startdate', models.DateTimeField(verbose_name=b'Start Date')),
                ('middate', models.DateTimeField(default=None, null=True, verbose_name=b'Mid Date', blank=True)),
                ('enddate', models.DateTimeField(verbose_name=b'End Date')),
                ('ante', fitcompetition.models.CurrencyField(verbose_name=b'Ante per player', max_digits=16, decimal_places=2)),
                ('reconciled', models.BooleanField(default=False)),
                ('disbursementAmount', fitcompetition.models.CurrencyField(default=0, null=True, max_digits=16, decimal_places=2, blank=True)),
                ('numWinners', models.IntegerField(default=0, null=True, blank=True)),
                ('totalDisbursed', fitcompetition.models.CurrencyField(default=0, null=True, max_digits=16, decimal_places=2, blank=True)),
                ('proofRequired', models.BooleanField(default=True)),
                ('account', models.ForeignKey(default=None, blank=True, to='fitcompetition.Account', null=True)),
                ('approvedActivities', models.ManyToManyField(to='fitcompetition.ActivityType', verbose_name=b'Approved Activity Types')),
            ],
        ),
        migrations.CreateModel(
            name='Challenger',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Joined', null=True)),
                ('challenge', models.ForeignKey(to='fitcompetition.Challenge')),
                ('fituser', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'fitcompetition_challenge_players',
            },
        ),
        migrations.CreateModel(
            name='FitnessActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uri', models.CharField(max_length=255)),
                ('duration', models.FloatField(default=0, null=True, blank=True)),
                ('date', models.DateTimeField(default=None, null=True, blank=True)),
                ('calories', models.FloatField(default=0, null=True, blank=True)),
                ('distance', models.FloatField(default=0, null=True, blank=True)),
                ('photo', models.ImageField(default=None, null=True, upload_to=fitcompetition.models.get_file_path, blank=True)),
                ('hasGPS', models.BooleanField(default=False)),
                ('hasProof', models.BooleanField(default=False)),
                ('cancelled', models.BooleanField(default=False)),
                ('type', models.ForeignKey(default=None, blank=True, to='fitcompetition.ActivityType', null=True)),
                ('user', models.ForeignKey(related_name='activities', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Fitness Activities',
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('captain', models.ForeignKey(related_name='captain', default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('challenge', models.ForeignKey(related_name='teams', to='fitcompetition.Challenge')),
                ('members', models.ManyToManyField(default=None, related_name='members', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(blank=True)),
                ('description', models.CharField(max_length=255)),
                ('amount', fitcompetition.models.CurrencyField(max_digits=16, decimal_places=2)),
                ('balance', fitcompetition.models.CurrencyField(default=None, null=True, max_digits=16, decimal_places=2, blank=True)),
                ('isCashflow', models.BooleanField(default=False, verbose_name=b'Is Cashflow In/Out')),
                ('stripeID', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('account', models.ForeignKey(to='fitcompetition.Account')),
            ],
        ),
        migrations.AddField(
            model_name='challenge',
            name='players',
            field=models.ManyToManyField(default=None, to=settings.AUTH_USER_MODEL, through='fitcompetition.Challenger', blank=True),
        ),
        migrations.AddField(
            model_name='fituser',
            name='account',
            field=models.ForeignKey(default=None, blank=True, to='fitcompetition.Account', null=True),
        ),
        migrations.AddField(
            model_name='fituser',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='fituser',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='challenger',
            unique_together=set([('fituser', 'challenge')]),
        ),
    ]
