"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os
import json
from ddt import ddt, data
from mock import patch
# from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.core.management import call_command
from social.apps.django_app.default.models import UserSocialAuth

from student.tests.factories import UserFactory
from courseware.tests.helpers import get_request_for_user

# from xmodule.course_module import CATALOG_VISIBILITY_ABOUT
# from xmodule.modulestore.django import clear_existing_modulestores
# from xmodule.modulestore.tests.factories import CourseFactory
# from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from eventtracking import tracker
from eventtracking.django import DjangoTracker
from xapi.xapi_tracker import XapiBackend
from xapi.tincan_wrapper import TinCanWrapper
from xapi.models import TrackingLog


SPLIT_COURSE_ID = "course-v1:ORG+COURSE+RUN"
COURSE_ID = 'ORG/COURSE/RUN'
TEST_UID = "test_social_uid"
TEST_HOMEPAGE_URL = "https://portal.ecolearning.eu"
TEST_USERNAME = "test-actor"
TEST_FILE_TRACKING = os.getcwd()+"/xapi/test_data/tracking.log"
TEST_BACKEND_OPTIONS = {
    "name": "default",
    "ID_COURSES": [SPLIT_COURSE_ID, COURSE_ID],  # list of course_id you want to track on LRS
    "USERNAME_LRS": "",  # username for the LRS endpoint
    "PASSWORD_LRS": "",  # password for the LRS endpoint
    "URL": "http://mylrs.endpoint/xAPI/statements",  # the LRS endpoint API URL
    "EXTRACTED_EVENT_NUMBER": 100,  # number of batch statements to extract from db and     sent in a job
    "HOMEPAGE_URL": TEST_HOMEPAGE_URL,
    "BASE_URL": "https://www.pok.polimi.it/",
    'OAI_PREFIX': 'oai:it.polimi.pok:'
}


class XapiTest(TestCase):   # pylint: disable=too-many-ancestors

    # MODULESTORE = settings.MODULESTORE

    @override_settings(FEATURES={'ENABLE_THIRD_PARTY_AUTH': True})
    def setUp(self):
        # super(XapiTest, self).setUp(create_user=False)
        super(XapiTest, self).setUp()
        # clear_existing_modulestores()
        self.tracker = DjangoTracker()
        tracker.register_tracker(self.tracker)
        # self.course = CourseFactory.create(
        #    org="ORG", course="COURSE", display_name="RUN",
        #    catalog_visibility=CATALOG_VISIBILITY_ABOUT
        # )
        user = UserFactory.create(username=TEST_USERNAME)
        UserSocialAuth.objects.create(user=user, provider="eco", uid=TEST_UID)
        self.user = user
        self.request = get_request_for_user(user)
        options = TEST_BACKEND_OPTIONS
        self.backend = XapiBackend(**options)
        self.tincanwrapper = TinCanWrapper(**options)

    def test_send_offline(self):
        args = []
        opts = {"filename": TEST_FILE_TRACKING, "course_ids": (",").join(TEST_BACKEND_OPTIONS.get("ID_COURSES"))}

        with patch('xapi.xapi_tracker.XapiBackend.get_context') as get_context:
            get_context.return_value = {}
            call_command('send_offline_data_2_tincan', *args, **opts)
            self.assertEqual(TrackingLog.objects.count(), 1)

            print "# Recall to check same event not added anymore"
            call_command('send_offline_data_2_tincan', *args, **opts)
            self.assertEqual(TrackingLog.objects.count(), 1)

    def test_get_actor(self):

        expected_actor = {
            "objectType": "Agent",
            "account": {
                "homePage": "%s?user=%s" % (TEST_HOMEPAGE_URL, TEST_UID),
                "name": TEST_UID
            }
        }
        actor = self.backend.get_actor(self.user.id)
        self.assertIsNotNone(actor)
        self.assertEqual(expected_actor, actor)

    def test_tincan(self):
        from tincan import Agent, AgentAccount
        account = AgentAccount(
            home_page="%s?user=%s" % (TEST_HOMEPAGE_URL, TEST_UID),
            name=TEST_UID
        )
        expected_actor = Agent(
            account=account
        )
        actor = self.backend.get_actor(self.user.id)
        self.assertIsNotNone(actor)
        self.assertEqual(expected_actor.to_json(), json.dumps(actor))


@ddt
class XapiMigrateTest(XapiTest):

    @override_settings(FEATURES={'ENABLE_THIRD_PARTY_AUTH': True})
    def setUp(self):
        super(XapiMigrateTest, self).setUp()
        raw_data = open(TEST_FILE_TRACKING).read()
        lines = [l.strip() for l in raw_data.split('\n') if l.strip() != '']
        self.basic_event = json.loads(lines[0])
        self.course_id = SPLIT_COURSE_ID

    def base_migrate_test(self, basic_event, course_id):
        verb_1, obj_1 = self.backend.to_xapi(basic_event, course_id)
        verb_2, obj_2 = self.tincanwrapper.to_xapi(basic_event, course_id)
        # self.assertIsNotNone(verb_1)
        # self.assertIsNotNone(obj_1)
        # self.assertIsNotNone(verb_2)
        # self.assertIsNotNone(obj_2)
        if verb_1 and verb_2:
            self.assertEqual(json.dumps(verb_1), verb_2.to_json())
            self.assertEqual(json.dumps(obj_1), obj_2.to_json())
        else:
            print "verbs NONE for basic_event: "+json.dumps(basic_event)
            print "verbs1 " + str(verb_1 is None)
            print "verbs2 " + str(verb_2 is None)


    @data(
        "/courses/"+SPLIT_COURSE_ID+"/info",
        "/courses/"+COURSE_ID+"/info",
        "/courses/"+SPLIT_COURSE_ID+"/about",
        "/courses/"+COURSE_ID+"/about"
    )
    def test_migrate_access_course(self, event_type):
        self.basic_event["event_type"] = event_type
        self.base_migrate_test(self.basic_event, self.course_id)

    @data(
        "/courses/"+SPLIT_COURSE_ID+"/courseware/122324",
        "/courses/"+COURSE_ID+"/courseware/122324",
        "/courses/"+SPLIT_COURSE_ID+"/courseware/",
        "/courses/"+COURSE_ID+"/courseware/"
    )
    def test_migrate_access_module(self, event_type):
        self.basic_event["event_type"] = event_type
        self.base_migrate_test(self.basic_event, self.course_id)

    @data(
        "edx.course.enrollment.activated",
        "edx.course.enrollment.deactivated"
    )
    @patch('xapi.utils.get_course_title')
    def test_migrate_enrollment(self, event_type, mock_get_course_title):
        self.basic_event["event_type"] = event_type
        self.basic_event["event_source"] = "server"

        mock_get_course_title.return_value = "COURSE_TITLE"
        self.base_migrate_test(self.basic_event, self.course_id)

    @data(
        "/courses/"+SPLIT_COURSE_ID+"/wiki/_create/***",
        "/courses/"+COURSE_ID+"/wiki/_create/",
        "/courses/"+SPLIT_COURSE_ID+"/wiki/UpdatePage/_edit/",
        "/courses/"+COURSE_ID+"/wiki/UpdatePage/_edit/",
        "/courses/"+SPLIT_COURSE_ID+"/wiki/APage/",
        "/courses/"+COURSE_ID+"/wiki/APage/",
    )
    def test_migrate_wiki(self, event_type):
        self.basic_event["event_type"] = event_type
        event = {"POST": {"title": ["WIKI_TITLE"]}}
        self.basic_event["event"] = event
        self.base_migrate_test(self.basic_event, self.course_id)

    @data(
        "/courses/"+SPLIT_COURSE_ID,
        "/courses/"+COURSE_ID
    )
    def test_migrate_access_problem(self, baseeventtype):
        event_type = baseeventtype
        event_type += "/xblock/block-v1:edx+Demo+demo+type@problem+block@__27"
        event_type += "/handler/xmodule_handler/problem_get"
        self.basic_event["event_type"] = event_type
        self.basic_event["event_source"] = "server"
        self.base_migrate_test(self.basic_event, self.course_id)

    def test_migrate_problem_check(self):
        self.basic_event["event_type"] = "problem_check"
        self.basic_event["event_source"] = "server"
        event = {"problem_id": "PROBLEM_ID"}
        context = {"module": {"display_name": "Quiz 1"}}
        self.basic_event["event"] = event
        self.basic_event["context"] = context
        self.base_migrate_test(self.basic_event, self.course_id)

    @data(
        "play_video",
        "load_video"
    )
    def test_migrate_video(self, event_type):
        self.basic_event["event_type"] = event_type
        self.basic_event["event_source"] = "browser"
        event = {"id": "VIDEO_ID"}
        self.basic_event["event"] = event
        self.base_migrate_test(self.basic_event, self.course_id)
