# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CourseStructureCache'
        db.create_table('ecoapi_coursestructurecache', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('course_id', self.gf('xmodule_django.models.CourseKeyField')(unique=True, max_length=255, db_index=True)),
            ('structure_json', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('ecoapi', ['CourseStructureCache'])


    def backwards(self, orm):
        # Deleting model 'CourseStructureCache'
        db.delete_table('ecoapi_coursestructurecache')


    models = {
        'ecoapi.coursestructurecache': {
            'Meta': {'object_name': 'CourseStructureCache'},
            'course_id': ('xmodule_django.models.CourseKeyField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'structure_json': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
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
