# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'OaiRecord.date_removed'
        db.add_column('oai_oairecord', 'date_removed',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'OaiRecord.date_removed'
        db.delete_column('oai_oairecord', 'date_removed')


    models = {
        'oai.oaierror': {
            'Meta': {'object_name': 'OaiError'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oai.OaiSource']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'oai.oaiformat': {
            'Meta': {'object_name': 'OaiFormat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'namespace': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'schema': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'})
        },
        'oai.oairecord': {
            'Meta': {'object_name': 'OaiRecord'},
            'date_removed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'format': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oai.OaiFormat']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'metadata': ('django.db.models.fields.TextField', [], {}),
            'sets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['oai.OaiSet']", 'symmetrical': 'False'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oai.OaiSource']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'oai.oaiset': {
            'Meta': {'object_name': 'OaiSet'},
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oai.OaiSource']", 'null': 'True', 'blank': 'True'})
        },
        'oai.oaisource': {
            'Meta': {'object_name': 'OaiSource'},
            'day_granularity': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'harvester': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_change': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'prefix': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '255'})
        },
        'oai.resumptiontoken': {
            'Meta': {'object_name': 'ResumptionToken'},
            'cursor': ('django.db.models.fields.IntegerField', [], {}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'fro': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'metadataPrefix': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oai.OaiFormat']", 'null': 'True', 'blank': 'True'}),
            'offset': ('django.db.models.fields.IntegerField', [], {}),
            'queryType': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oai.OaiSet']", 'null': 'True', 'blank': 'True'}),
            'total_count': ('django.db.models.fields.IntegerField', [], {}),
            'until': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['oai']