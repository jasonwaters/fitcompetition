# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ActivityType'
        db.create_table(u'fitcompetition_activitytype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'fitcompetition', ['ActivityType'])

        # Deleting field 'Goal.isActive'
        db.delete_column(u'fitcompetition_goal', 'isActive')

        # Adding M2M table for field approvedActivities on 'Goal'
        m2m_table_name = db.shorten_name(u'fitcompetition_goal_approvedactivities')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('goal', models.ForeignKey(orm[u'fitcompetition.goal'], null=False)),
            ('activitytype', models.ForeignKey(orm[u'fitcompetition.activitytype'], null=False))
        ))
        db.create_unique(m2m_table_name, ['goal_id', 'activitytype_id'])


        if not db.dry_run:
            orm.ActivityType.objects.create(name="Running")
            orm.ActivityType.objects.create(name="Cycling")
            orm.ActivityType.objects.create(name="Mountain Biking")
            orm.ActivityType.objects.create(name="Walking")
            orm.ActivityType.objects.create(name="Hiking")
            orm.ActivityType.objects.create(name="Downhill Skiing")
            orm.ActivityType.objects.create(name="Cross-Country Skiing")
            orm.ActivityType.objects.create(name="Snowboarding")
            orm.ActivityType.objects.create(name="Skating")
            orm.ActivityType.objects.create(name="Swimming")
            orm.ActivityType.objects.create(name="Wheelchair")
            orm.ActivityType.objects.create(name="Rowing")
            orm.ActivityType.objects.create(name="Elliptical")
            orm.ActivityType.objects.create(name="Other")


    def backwards(self, orm):
        # Deleting model 'ActivityType'
        db.delete_table(u'fitcompetition_activitytype')

        # Adding field 'Goal.isActive'
        db.add_column(u'fitcompetition_goal', 'isActive',
                      self.gf('fitcompetition.models.UniqueBooleanField')(default=False),
                      keep_default=False)

        # Removing M2M table for field approvedActivities on 'Goal'
        db.delete_table(db.shorten_name(u'fitcompetition_goal_approvedactivities'))


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
        u'fitcompetition.goal': {
            'Meta': {'object_name': 'Goal'},
            'ante': ('fitcompetition.models.CurrencyField', [], {'max_digits': '16', 'decimal_places': '2'}),
            'approvedActivities': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['fitcompetition.ActivityType']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'distance': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '2'}),
            'enddate': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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