# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Teacher'
        db.create_table('ecoapi_teacher', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('id_teacher', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('image', self.gf('django.db.models.fields.URLField')(max_length=1024, null=True, blank=True)),
        ))
        db.send_create_signal('ecoapi', ['Teacher'])

        # Adding model 'TeacherDescription'
        db.create_table('ecoapi_teacherdescription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecoapi.Teacher'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('label', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('ecoapi', ['TeacherDescription'])

        # Adding unique constraint on 'TeacherDescription', fields ['teacher', 'language']
        db.create_unique('ecoapi_teacherdescription', ['teacher_id', 'language'])


    def backwards(self, orm):
        # Removing unique constraint on 'TeacherDescription', fields ['teacher', 'language']
        db.delete_unique('ecoapi_teacherdescription', ['teacher_id', 'language'])

        # Deleting model 'Teacher'
        db.delete_table('ecoapi_teacher')

        # Deleting model 'TeacherDescription'
        db.delete_table('ecoapi_teacherdescription')


    models = {
        'ecoapi.teacher': {
            'Meta': {'object_name': 'Teacher'},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_teacher': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'image': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'ecoapi.teacherdescription': {
            'Meta': {'unique_together': "(['teacher', 'language'],)", 'object_name': 'TeacherDescription'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecoapi.Teacher']"})
        }
    }
