# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        if not db.dry_run:
            users = orm.FitUser.objects.all()
            for user in users:
                if user.username.startswith('rkpr_'):
                    user.integrationName = "Runkeeper"
                elif user.username.startswith('mmf_'):
                    user.integrationName = "MapMyFitness"
                elif user.username.startswith('strv_'):
                    user.integrationName = "Strava"
                user.save()

    def backwards(self, orm):
        pass

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'fitcompetition.account': {
            'Meta': {'object_name': 'Account'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'fitcompetition.activitytype': {
            'Meta': {'object_name': 'ActivityType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'fitcompetition.challenge': {
            'Meta': {'object_name': 'Challenge'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['fitcompetition.Account']", 'null': 'True', 'blank': 'True'}),
            'ante': ('fitcompetition.models.CurrencyField', [], {'max_digits': '16', 'decimal_places': '2'}),
            'approvedActivities': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['fitcompetition.ActivityType']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'disbursementAmount': ('fitcompetition.models.CurrencyField', [], {'default': '0', 'null': 'True', 'max_digits': '16', 'decimal_places': '2', 'blank': 'True'}),
            'distance': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '2'}),
            'enddate': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'middate': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'numWinners': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['fitcompetition.FitUser']", 'through': u"orm['fitcompetition.Challenger']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'reconciled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'startdate': ('django.db.models.fields.DateTimeField', [], {}),
            'style': ('django.db.models.fields.CharField', [], {'default': "'ALL'", 'max_length': '6'}),
            'totalDisbursed': ('fitcompetition.models.CurrencyField', [], {'default': '0', 'null': 'True', 'max_digits': '16', 'decimal_places': '2', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'INDV'", 'max_length': '6'})
        },
        u'fitcompetition.challenger': {
            'Meta': {'unique_together': "(('fituser', 'challenge'),)", 'object_name': 'Challenger', 'db_table': "'fitcompetition_challenge_players'"},
            'challenge': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fitcompetition.Challenge']"}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'fituser': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fitcompetition.FitUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'fitcompetition.fitnessactivity': {
            'Meta': {'object_name': 'FitnessActivity'},
            'calories': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'distance': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'hasGPS': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'default': 'None', 'max_length': '100', 'null': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['fitcompetition.ActivityType']", 'null': 'True', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fitcompetition.FitUser']"})
        },
        u'fitcompetition.fituser': {
            'Meta': {'ordering': "['fullname']", 'object_name': 'FitUser'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['fitcompetition.Account']", 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'fullname': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'integrationName': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lastExternalSyncDate': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mapmyfitnessToken': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'mapmyfitnessTokenSecret': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'medium_picture': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'normal_picture': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phoneNumber': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'profile_url': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'runkeeperToken': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'stravaToken': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'fitcompetition.team': {
            'Meta': {'object_name': 'Team'},
            'captain': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'captain'", 'null': 'True', 'blank': 'True', 'to': u"orm['fitcompetition.FitUser']"}),
            'challenge': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fitcompetition.Challenge']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'members'", 'default': 'None', 'to': u"orm['fitcompetition.FitUser']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'fitcompetition.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fitcompetition.Account']"}),
            'amount': ('fitcompetition.models.CurrencyField', [], {'max_digits': '16', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isCashflow': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['fitcompetition']