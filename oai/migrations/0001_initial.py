# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'OaiSource'
        db.create_table('oai_oaisource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('prefix', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')()),
            ('day_granularity', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('harvester', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('last_change', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('oai', ['OaiSource'])

        # Adding model 'OaiError'
        db.create_table('oai_oaierror', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oai.OaiSource'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
        ))
        db.send_create_signal('oai', ['OaiError'])

        # Adding model 'OaiSet'
        db.create_table('oai_oaiset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oai.OaiSource'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('fullname', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
        ))
        db.send_create_signal('oai', ['OaiSet'])

        # Adding model 'OaiFormat'
        db.create_table('oai_oaiformat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('schema', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('namespace', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
        ))
        db.send_create_signal('oai', ['OaiFormat'])

        # Adding model 'OaiRecord'
        db.create_table('oai_oairecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oai.OaiSource'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('format', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oai.OaiFormat'])),
            ('identifier', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('metadata', self.gf('django.db.models.fields.TextField')()),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('oai', ['OaiRecord'])

        # Adding M2M table for field sets on 'OaiRecord'
        db.create_table('oai_oairecord_sets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('oairecord', models.ForeignKey(orm['oai.oairecord'], null=False)),
            ('oaiset', models.ForeignKey(orm['oai.oaiset'], null=False))
        ))
        db.create_unique('oai_oairecord_sets', ['oairecord_id', 'oaiset_id'])

        # Adding model 'ResumptionToken'
        db.create_table('oai_resumptiontoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('queryType', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oai.OaiSet'], null=True, blank=True)),
            ('metadataPrefix', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oai.OaiFormat'], null=True, blank=True)),
            ('fro', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('until', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('offset', self.gf('django.db.models.fields.IntegerField')()),
            ('cursor', self.gf('django.db.models.fields.IntegerField')()),
            ('total_count', self.gf('django.db.models.fields.IntegerField')()),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('oai', ['ResumptionToken'])


    def backwards(self, orm):
        # Deleting model 'OaiSource'
        db.delete_table('oai_oaisource')

        # Deleting model 'OaiError'
        db.delete_table('oai_oaierror')

        # Deleting model 'OaiSet'
        db.delete_table('oai_oaiset')

        # Deleting model 'OaiFormat'
        db.delete_table('oai_oaiformat')

        # Deleting model 'OaiRecord'
        db.delete_table('oai_oairecord')

        # Removing M2M table for field sets on 'OaiRecord'
        db.delete_table('oai_oairecord_sets')

        # Deleting model 'ResumptionToken'
        db.delete_table('oai_resumptiontoken')


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