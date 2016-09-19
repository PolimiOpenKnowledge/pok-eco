# -*- coding: utf-8 -*-
import re
import json
from datetime import date
from os.path import splitext

from django.db import models
from model_utils.models import TimeStampedModel
from util.models import CompressedTextField
from xmodule_django.models import CourseKeyField


def sanitize_basename(unsafe_basename):
    """
    Requires a string like 'filename.extension'
    """
    filename, extension = splitext(unsafe_basename)
    sanitized_filename = sanitize_string(filename)
    return sanitized_filename + extension


def sanitize_string(unsafe_string):
    """
    Removes all non-word characters from a string
    Returns a string with only [a-zA-Z0-9_] characters
    """
    return re.sub(r'\W', '_', unsafe_string)


def sanitized_upload_to(instance, unsafe_basename):
    """
    To be used as function in ImageField 'upload_to'. The second argument is
    in the form 'filename.extension', no path is available.
    """
    model_name = sanitize_string(instance.__class__.__name__).lower()
    anno = date.today().year
    filename = sanitize_basename(unsafe_basename)
    return u'%s/%d/%s' % (model_name, anno, filename)


LINGUE = (
    ('en', 'English'),
    ('it', 'Italiano'),
)


class Teacher(models.Model):
    # Internal id of the teacher. This id can be obtained from the OAI­PMH ListRecords response,
    # which gives teacher information in vcard format.
    id_teacher = models.CharField(max_length=64, unique=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    image = models.URLField(max_length=1024, null=True, blank=True, help_text='URL of the teacher\'s image')

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)


class TeacherDescription(models.Model):
    teacher = models.ForeignKey(Teacher)
    language = models.CharField(max_length=2, choices=LINGUE)
    label = models.TextField()

    class Meta(object):
        unique_together = ['teacher', 'language']
        app_label = 'xapi'


class CourseStructureCache(TimeStampedModel):
    course_id = CourseKeyField(max_length=255, db_index=True, unique=True, verbose_name='Course ID')
    structure_json = CompressedTextField(verbose_name='Structure JSON', blank=True, null=True)

    @property
    def structure(self):
        if self.structure_json:
            return json.loads(self.structure_json)
        return None
