# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Goal.enddate'
        db.alter_column(u'fitcompetition_goal', 'enddate', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'Goal.startdate'
        db.alter_column(u'fitcompetition_goal', 'startdate', self.gf('django.db.models.fields.DateTimeField')())

    def backwards(self, orm):

        # Changing field 'Goal.enddate'
        db.alter_column(u'fitcompetition_goal', 'enddate', self.gf('django.db.models.fields.DateField')())

        # Changing field 'Goal.startdate'
        db.alter_column(u'fitcompetition_goal', 'startdate', self.gf('django.db.models.fields.DateField')())

    models = {
        u'fitcompetition.goal': {
            'Meta': {'object_name': 'Goal'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'distance': ('django.db.models.fields.IntegerField', [], {}),
            'enddate': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isActive': ('fitcompetition.models.UniqueBooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'startdate': ('django.db.models.fields.DateTimeField', [], {})
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