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
import json

from social.apps.django_app.default.models import UserSocialAuth
from tincan import (
    Activity,
    ActivityDefinition,
    Agent,
    AgentAccount,
    Context,
    ContextActivities,
    Extensions,
    LanguageMap,
    Statement
)
from track.backends import BaseBackend
from track.utils import DateTimeJSONEncoder
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
        actor = Agent(
            account=AgentAccount(
                homePage="%s?user=%s" % (self.homepage_url, usereco.uid),
                name=usereco.uid
            )
        )
        return actor

    def get_context(self, course_id, user_id):
        parents = []
        title = xutils.get_course_title(course_id)
        description = xutils.get_course_description(course_id, user_id)
        course_parent = Activity(
            id=self.oai_prefix + course_id,
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': title}),
                description=LanguageMap({'en-US': description}),
                type="http://adlnet.gov/expapi/activities/course"
            )
        )
        parents.append(course_parent)
        context = Context(
            contextActivities=ContextActivities(
                parent=parents
            ),
            extensions=Extensions({})
        )
        return context

    def send(self, event_edx):
        if not self.is_enabled():
            log.warn("Xapi Backend disabled")
            return
        else:
            self.process_event(event_edx)

    def process_event(self, event_edx):
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
                timepart = event_edx['time']
                timestamp = xutils.make_datetime_for_tincan(timepart)

                actor = None
                user_id = 0
                try:
                    user_id = event_edx['context'].get('user_id', 0)
                except:
                    user_id = json.loads(event_edx['context']).get('user_id', 0)
                try:
                    actor = self.get_actor(user_id)
                except (ValueError, UserSocialAuth.DoesNotExist) as e:
                    # Only logged ECO user need to be tracked
                    return

                verb, obj = self.to_xapi(event_edx, course_id)

                context = self.get_context(course_id, user_id)
                d = {"time_with_millis": timepart}
                context.extensions = Extensions(d)
                # verb = None means to not record the action
                if verb:
                    statement = Statement(
                        actor=actor,
                        verb=verb,
                        object=obj,
                        context=context,
                        timestamp=timestamp
                    )

                    tldat = TrackingLog(
                        dtcreated=timestamp,
                        user_id=user_id,
                        course_id=course_id,
                        statement=statement.to_json(),
                        original_event=json.dumps(event_edx, cls=DateTimeJSONEncoder)
                    )

                    # We don't need to add duplication event test, so we save directly
                    tldat.save()

            except Exception as e:  # pylint: disable=broad-except
                log.exception(e)
        else:
            if course_id != '':
                # print 'Course not activated', course_id  # Uncomment for debug
                pass
