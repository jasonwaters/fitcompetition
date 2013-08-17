# -*- coding: utf-8 -*-
from datetime import datetime
from fitcompetition.models import Transaction
from fitcompetition.settings import TIME_ZONE
import pytz
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Deleting field 'Challenger.hasPaid'
        db.delete_column('fitcompetition_challenge_players', 'hasPaid')

        if not db.dry_run:
            #everybody except tayler, tyson and jenny
            fitusers = orm.FitUser.objects.exclude(username__in=['admin', '21678544', '21634788', '9685555'])
            for fituser in fitusers:
                now = datetime.now(tz=pytz.timezone(TIME_ZONE))
                orm.Transaction.objects.create(date=now,
                                               user=fituser,
                                               description="Deposit",
                                               amount=16.66)

    def backwards(self, orm):
        # Adding field 'Challenger.hasPaid'
        db.add_column('fitcompetition_challenge_players', 'hasPaid',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [],
                            {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')",
                     'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': (
                'django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)",
                     'object_name': 'ContentType', 'db_table': "'django_content_type'"},
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
            'approvedActivities': ('django.db.models.fields.related.ManyToManyField', [],
                                   {'to': u"orm['fitcompetition.ActivityType']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'distance': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '2'}),
            'enddate': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'players': ('django.db.models.fields.related.ManyToManyField', [],
                        {'default': 'None', 'to': u"orm['fitcompetition.FitUser']",
                         'through': u"orm['fitcompetition.Challenger']", 'blank': 'True', 'symmetrical': 'False',
                         'null': 'True'}),
            'startdate': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'fitcompetition.challenger': {
            'Meta': {'unique_together': "(('fituser', 'challenge'),)", 'object_name': 'Challenger',
                     'db_table': "'fitcompetition_challenge_players'"},
            'challenge': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fitcompetition.Challenge']"}),
            'date_joined': (
                'django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'fituser': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fitcompetition.FitUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'fitcompetition.fitnessactivity': {
            'Meta': {'object_name': 'FitnessActivity'},
            'calories': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'distance': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [],
                     {'default': 'None', 'to': u"orm['fitcompetition.ActivityType']", 'null': 'True', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fitcompetition.FitUser']"})
        },
        u'fitcompetition.fituser': {
            'Meta': {'ordering': "['fullname']", 'object_name': 'FitUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'fullname': ('django.db.models.fields.CharField', [],
                         {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [],
                       {'default': 'None', 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [],
                       {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lastHealthGraphUpdate': (
                'django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'medium_picture': ('django.db.models.fields.CharField', [],
                               {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'normal_picture': ('django.db.models.fields.CharField', [],
                               {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phoneNumber': ('django.db.models.fields.CharField', [],
                            {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'profile_url': ('django.db.models.fields.CharField', [],
                            {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'runkeeperToken': ('django.db.models.fields.CharField', [],
                               {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [],
                                 {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'fitcompetition.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'amount': ('fitcompetition.models.CurrencyField', [], {'max_digits': '16', 'decimal_places': '2'}),
            'challenge': ('django.db.models.fields.related.ForeignKey', [],
                          {'default': 'None', 'to': u"orm['fitcompetition.Challenge']", 'null': 'True',
                           'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fitcompetition.FitUser']"})
        }
    }

    complete_apps = ['fitcompetition']