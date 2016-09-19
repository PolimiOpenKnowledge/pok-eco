# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import util.models
import django.utils.timezone
import model_utils.fields
import xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CourseStructureCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('course_id', xmodule_django.models.CourseKeyField(unique=True, max_length=255, verbose_name=b'Course ID', db_index=True)),
                ('structure_json', util.models.CompressedTextField(null=True, verbose_name=b'Structure JSON', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('id_teacher', models.CharField(unique=True, max_length=64)),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
                ('image', models.URLField(help_text=b"URL of the teacher's image", max_length=1024, null=True, blank=True)),
            ],
        ),
    ]
