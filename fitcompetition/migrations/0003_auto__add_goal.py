# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Goal'
        db.create_table(u'fitcompetition_goal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('distance', self.gf('django.db.models.fields.IntegerField')()),
            ('startdate', self.gf('django.db.models.fields.DateField')()),
            ('enddate', self.gf('django.db.models.fields.DateField')()),
            ('isActive', self.gf('fitcompetition.models.UniqueBooleanField')(default=False)),
        ))
        db.send_create_signal(u'fitcompetition', ['Goal'])


    def backwards(self, orm):
        # Deleting model 'Goal'
        db.delete_table(u'fitcompetition_goal')


    models = {
        u'fitcompetition.goal': {
            'Meta': {'object_name': 'Goal'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'distance': ('django.db.models.fields.IntegerField', [], {}),
            'enddate': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isActive': ('fitcompetition.models.UniqueBooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'startdate': ('django.db.models.fields.DateField', [], {})
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