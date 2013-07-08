# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'FitnessActivity.distance'
        db.alter_column(u'fitcompetition_fitnessactivity', 'distance', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'FitnessActivity.calories'
        db.alter_column(u'fitcompetition_fitnessactivity', 'calories', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'FitnessActivity.duration'
        db.alter_column(u'fitcompetition_fitnessactivity', 'duration', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'FitnessActivity.date'
        db.alter_column(u'fitcompetition_fitnessactivity', 'date', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Renaming column for 'FitnessActivity.type' to match new field type.
        db.rename_column(u'fitcompetition_fitnessactivity', 'type', 'type_id')
        # Changing field 'FitnessActivity.type'
        db.alter_column(u'fitcompetition_fitnessactivity', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fitcompetition.ActivityType']))
        # Adding index on 'FitnessActivity', fields ['type']
        db.create_index(u'fitcompetition_fitnessactivity', ['type_id'])


    def backwards(self, orm):
        # Removing index on 'FitnessActivity', fields ['type']
        db.delete_index(u'fitcompetition_fitnessactivity', ['type_id'])


        # Changing field 'FitnessActivity.distance'
        db.alter_column(u'fitcompetition_fitnessactivity', 'distance', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'FitnessActivity.calories'
        db.alter_column(u'fitcompetition_fitnessactivity', 'calories', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'FitnessActivity.duration'
        db.alter_column(u'fitcompetition_fitnessactivity', 'duration', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'FitnessActivity.date'
        db.alter_column(u'fitcompetition_fitnessactivity', 'date', self.gf('django.db.models.fields.DateTimeField')(default=None))

        # Renaming column for 'FitnessActivity.type' to match new field type.
        db.rename_column(u'fitcompetition_fitnessactivity', 'type_id', 'type')
        # Changing field 'FitnessActivity.type'
        db.alter_column(u'fitcompetition_fitnessactivity', 'type', self.gf('django.db.models.fields.CharField')(max_length=255))

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
        u'fitcompetition.activitytype': {
            'Meta': {'object_name': 'ActivityType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'fitcompetition.challenge': {
            'Meta': {'object_name': 'Challenge'},
            'ante': ('fitcompetition.models.CurrencyField', [], {'max_digits': '16', 'decimal_places': '2'}),
            'approvedActivities': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['fitcompetition.ActivityType']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'distance': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '2'}),
            'enddate': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['fitcompetition.FitUser']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            'startdate': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'fitcompetition.fitnessactivity': {
            'Meta': {'object_name': 'FitnessActivity'},
            'calories': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'distance': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fitcompetition.ActivityType']"}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fitcompetition.FitUser']"})
        },
        u'fitcompetition.fituser': {
            'Meta': {'object_name': 'FitUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'medium_picture': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'normal_picture': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'profile_url': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'runkeeperToken': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'fitcompetition.runkeeperrecord': {
            'Meta': {'object_name': 'RunkeeperRecord'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'userID': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['fitcompetition']