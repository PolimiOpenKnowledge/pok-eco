# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackingLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dtcreated', models.DateTimeField(verbose_name=b'creation date', db_index=True)),
                ('user_id', models.IntegerField(db_index=True, blank=True)),
                ('course_id', xmodule_django.models.CourseKeyField(max_length=255, blank=True)),
                ('original_event', models.TextField(blank=True)),
                ('statement', models.TextField(blank=True)),
                ('tincan_key', models.CharField(max_length=512, null=True, blank=True)),
                ('tincan_error', models.TextField(default=b'', null=True, blank=True)),
                ('exported', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'xapi_trackinglog',
            },
        ),
        migrations.CreateModel(
            name='XapiBackendConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('change_date', models.DateTimeField(auto_now_add=True, verbose_name='Change date')),
                ('enabled', models.BooleanField(default=False, verbose_name='Enabled')),
                ('id_courses', models.TextField(help_text=b'A comma separated list of course_id you want to track on LRS', verbose_name=b'ID_COURSES', blank=True)),
                ('lrs_api_url', models.URLField(help_text=b'The LRS endpoint API URL', verbose_name=b'LRS API URL', blank=True)),
                ('username_lrs', models.TextField(help_text=b'username for the LRS endpoint', verbose_name=b'USERNAME_LRS', blank=True)),
                ('password_lrs', models.TextField(help_text=b'password for the LRS endpoint', verbose_name=b'PASSWORD_LRS', blank=True)),
                ('oai_prefix', models.CharField(help_text=b'the oai prefix course (eg oai:it.polimi.pok:)', max_length=100, verbose_name=b'OAI_PREFIX', blank=True)),
                ('user_profile_home_url', models.URLField(help_text=b'homepage url for user profile (third party auth)', verbose_name=b'HOMEPAGE_URL', blank=True)),
                ('base_url', models.URLField(help_text=b'base url for lms platform', verbose_name=b'BASE_URL', blank=True)),
                ('extracted_event_number', models.IntegerField(default=50, help_text=b'The maximum number of extracted event to send each iteration', verbose_name=b'EXTRACTED EVENT NUMBER')),
                ('changed_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='Changed by')),
            ],
            options={
                'ordering': ('-change_date',),
                'abstract': False,
            },
        ),
    ]
