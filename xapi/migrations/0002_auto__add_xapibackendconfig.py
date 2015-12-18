# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'XapiBackendConfig'
        db.create_table('xapi_xapibackendconfig', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.PROTECT)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id_courses', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('lrs_api_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('username_lrs', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('password_lrs', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('oai_prefix', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('user_profile_home_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('base_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('extracted_event_number', self.gf('django.db.models.fields.IntegerField')(default=50)),
        ))
        db.send_create_signal('xapi', ['XapiBackendConfig'])


    def backwards(self, orm):
        # Deleting model 'XapiBackendConfig'
        db.delete_table('xapi_xapibackendconfig')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'xapi.trackinglog': {
            'Meta': {'object_name': 'TrackingLog'},
            'course_id': ('xmodule_django.models.CourseKeyField', [], {'max_length': '255', 'blank': 'True'}),
            'dtcreated': ('django.db.models.fields.DateTimeField', [], {}),
            'exported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_event': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'statement': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tincan_error': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'tincan_key': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'blank': 'True'})
        },
        'xapi.xapibackendconfig': {
            'Meta': {'ordering': "('-change_date',)", 'object_name': 'XapiBackendConfig'},
            'base_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'extracted_event_number': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_courses': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'lrs_api_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'oai_prefix': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'password_lrs': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user_profile_home_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'username_lrs': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['xapi']
