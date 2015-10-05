from __future__ import absolute_import

import logging
# import datetime
import json

from django.db import models

from track.backends import BaseBackend
from xmodule_django.models import CourseKeyField

from social.apps.django_app.default.models import UserSocialAuth
from courseware.courses import get_course_by_id, get_course_about_section
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xapi.patterns import (
    AccessCourseRule
)


class TinCanWrapper(object):
    """Wrap edx event and translate to tincan with a set of rules"""

    def __init__(self, **options):
        """
        Configure wrapper used by the backend.
        """

        # super(TinCanWrapper, self).__init__(**options)
        self.patterns = [AccessCourseRule(**options)]

    def to_xapi(self, evt, course_id):
        """
        Convert edx event using a list of patterns to convert. First match win
        """
        for p in self.patterns:
            if (p.match(evt, course_id)):
                return p.convert(evt, course_id)
