# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TrackingLog'
        db.create_table('xapi_trackinglog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dtcreated', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')(blank=True, db_index=True)),
            ('course_id', self.gf('xmodule_django.models.CourseKeyField')(max_length=255, blank=True)),
            ('original_event', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('statement', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('tincan_key', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('tincan_error', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('exported', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('xapi', ['TrackingLog'])


    def backwards(self, orm):
        # Deleting model 'TrackingLog'
        db.delete_table('xapi_trackinglog')


    models = {
        'xapi.trackinglog': {
            'Meta': {'object_name': 'TrackingLog'},
            'course_id': ('xmodule_django.models.CourseKeyField', [], {'max_length': '255', 'blank': 'True'}),
            'dtcreated': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'exported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_event': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'statement': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tincan_error': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'tincan_key': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'db_index': 'True'})
        }
    }

    complete_apps = ['xapi']
