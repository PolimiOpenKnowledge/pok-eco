# pylint: disable=W1401,W0702,E1002
# -*- coding: utf-8 -*-
"""
Event tracker backend that saves events to a Django database before send
them on LRS.
"""

# TODO: this module is very specific to the event schema, and is only
# brought here for legacy support. It should be updated when the
# schema changes or eventually deprecated.

from __future__ import absolute_import

import logging
# import datetime
import json

from social.apps.django_app.default.models import UserSocialAuth

from track.backends import BaseBackend
from courseware.courses import get_course_about_section
from xapi.models import TrackingLog
import xapi.utils as xutils
from xapi.tincan_wrapper import TinCanWrapper

# TODO: è giusto? era così:
# log = logging.getLogger('track.backends.django')
log = logging.getLogger('xapi.xapi_tracker')


class XapiBackend(BaseBackend):
    """Event tracker backend that saves to a Django database"""

    def __init__(self, name='default', **options):
        """
        Configure database used by the backend.
        :Parameters:
          - `name` is the name of the database as specified in the project
            settings.
        """

        super(XapiBackend, self).__init__(**options)

        self.name = name
        self.tincan = TinCanWrapper()

    @property
    def homepage_url(self):
        return self.backend_setting('user_profile_home_url', '')

    @property
    def course_ids(self):
        return self.backend_setting('id_courses', [])

    @property
    def oai_prefix(self):
        return self.backend_setting('oai_prefix', [])

    def is_enabled(self):
        return self.backend_setting('enabled', False)

    #  pylint: disable=attribute-defined-outside-init
    def backend_setting(self, setting_name, default=None):
        """ Get a setting, from XapiBackendConfig """
        from xapi.models import XapiBackendConfig
        self.config = XapiBackendConfig.current()
        if hasattr(self.config, str(setting_name)):
            return getattr(self.config, str(setting_name))
        else:
            return default

    # See https://github.com/adlnet/edx-xapi-bridge/blob/master/xapi-bridge/converter.py
    def to_xapi(self, evt, course_id):
        return self.tincan.to_xapi(evt, course_id)

    def get_actor(self, user_id):
        # View http://192.168.33.10:8000/admin/default/usersocialauth/
        # No need to check existance, because is mandatory
        usereco = UserSocialAuth.objects.get(user=user_id)

        actor = {
            "objectType": "Agent",
            "account": {
                "homePage": "%s?user=%s" % (self.homepage_url, usereco.uid),
                "name": usereco.uid
            }
        }
        return actor

    def get_context(self, course_id):
        parents = []
        course = xutils.get_course(course_id)
        title = get_course_about_section(course, "title")
        description = get_course_about_section(course, "short_description")
        course_parent = {
            "id":  self.oai_prefix + course_id,
            "objectType": "Activity",
            "definition": {
                "name": {
                    "en-US": title
                },
                "description": {
                    "en-US": description
                },
                "type": "http://adlnet.gov/expapi/activities/course"
            }
        }
        parents.append(course_parent)

        context = {
            "contextActivities": {
                "parent": parents
            }
        }
        return context

    def send(self, event_edx):
        if not self.is_enabled():
            log.warn("Xapi Backend disabled")
            return
        course_id = event_edx['context'].get('course_id', None)
        if course_id is None or course_id == '':
            try:
                # We need to do this because we receive a string instead than a dictionary
                event = json.loads(event_edx['event'])
                course_id = event['POST'].get('course_id', None)[0]
            except:
                pass  # No event data, just skip
        if course_id != '' and course_id in self.course_ids:
            try:
                # Sometimes we receive time as python datetime, sometimes as string...
                try:
                    timestamp = event_edx['time'].isoformat()  # ststrftime("%Y-%m-%dT%H:%M:%S%f%z")
                except AttributeError:
                    timestamp = event_edx['time']
                actor = None
                try:
                    actor = self.get_actor(event_edx['context']['user_id'])
                except (ValueError, UserSocialAuth.DoesNotExist) as e:
                    # Only logged ECO user need to be tracked
                    return

                verb, obj = self.to_xapi(event_edx, course_id)

                context = self.get_context(course_id)
                # verb = None means to not record the action
                if verb:
                    statement = {
                        'actor': actor,
                        'verb': verb.to_json(),
                        'object': obj.to_json(),
                        'timestamp': timestamp,
                        'context': context
                    }

                    tldat = TrackingLog(
                        dtcreated=timestamp,  # event_edx['time'],
                        user_id=event_edx['context']['user_id'],
                        course_id=course_id,
                        statement=json.dumps(statement),
                        original_event=event_edx
                    )

                    # We don't need to add duplication event test, so we save directly
                    tldat.save()

            except Exception as e:  # pylint: disable=broad-except
                log.exception(e)
        else:
            if course_id != '':
                # print 'Course not activated', course_id  # Uncomment for debug
                pass
