"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os
import json
from ddt import ddt, data
from datetime import datetime
from pytz import UTC
from mock import patch
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import unittest
from django.core.management import call_command
from social.apps.django_app.default.models import UserSocialAuth

from student.tests.factories import UserFactory
from courseware.tests.helpers import get_request_for_user

from eventtracking import tracker
from eventtracking.django import DjangoTracker
from xapi.xapi_tracker import XapiBackend
from xapi.tincan_wrapper import TinCanWrapper
from xapi.models import TrackingLog
from xapi.patterns import (
    AccessCourseRule,
    AccessModuleRule,
    AccessProblemRule,
    AccessWikiRule,
    AccessWikiPageRule,
    CreateWikiRule,
    EditWikiRule,
    ForumAccessRule,
    ForumCreateThreadRule,
    ForumLikesRule,
    ForumReadsRule,
    ForumReplyRule,
    LearnerEnrollMOOCRule,
    LearnerUnEnrollMOOCRule,
    LoadVideoRule,
    PlayVideoRule,
    ProblemCheckRule,
    AccessPeerAssessmentRule,
    SubmitsPeerAssessmentRule,
    SubmitsPeerFeedbackRule,
    SubmitsSelfFeedbackRule
)
from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.eco_verbs import LearnerAccessesMoocVerb


SPLIT_COURSE_ID = "course-v1:ORG+COURSE+RUN"
COURSE_ID = 'ORG/COURSE/RUN'
TEST_UID = "test_social_uid"
TEST_HOMEPAGE_URL = "https://portal.ecolearning.eu"
TEST_USERNAME = "test-actor"
TEST_FILE_TRACKING = os.getcwd()+"/xapi/test_data/tracking.log"
TEST_FILE_TRACKING_OFFLINE = os.getcwd()+"/xapi/test_data/tracking_offline.log"
TEST_BACKEND_OPTIONS = {
    "name": "xapi",
    "ID_COURSES": [SPLIT_COURSE_ID, COURSE_ID],  # list of course_id you want to track on LRS
    "USERNAME_LRS": os.environ.get('XAPI_USERNAME_LRS', ""),  # username for the LRS endpoint
    "PASSWORD_LRS": os.environ.get('XAPI_PASSWORD_LRS', ""),  # password for the LRS endpoint
    "URL": os.environ.get('XAPI_URL_LRS', ""),  # the LRS endpoint API URL
    "EXTRACTED_EVENT_NUMBER": 100,  # number of batch statements to extract from db and     sent in a job
    "HOMEPAGE_URL": TEST_HOMEPAGE_URL,
    "BASE_URL": "https://www.pok.polimi.it/",
    'OAI_PREFIX': 'oai:it.polimi.pok:'
}
XAPI_BACKEND_SETTINGS = {
    'xapi': {
        'ENGINE': 'xapi.xapi_tracker.XapiBackend',
        'OPTIONS': TEST_BACKEND_OPTIONS
    }
}


class XapiTest(TestCase):   # pylint: disable=too-many-ancestors

    @override_settings(FEATURES={'ENABLE_THIRD_PARTY_AUTH': True})
    def setUp(self):
        super(XapiTest, self).setUp()
        self.tracker = DjangoTracker()
        tracker.register_tracker(self.tracker)
        user = UserFactory.create(username=TEST_USERNAME)
        UserSocialAuth.objects.create(user=user, provider="eco", uid=TEST_UID)
        self.user = user
        self.request = get_request_for_user(user)
        options = TEST_BACKEND_OPTIONS
        self.backend = XapiBackend(**options)
        self.tincanwrapper = TinCanWrapper(**options)

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


class XapiSendOfflineTest(XapiTest):
    def setUp(self):
        super(XapiSendOfflineTest, self).setUp()

    def test_send_offline(self):
        args = []
        opts = {"filename": TEST_FILE_TRACKING_OFFLINE,
                "course_ids": (",").join(TEST_BACKEND_OPTIONS.get("ID_COURSES"))}
        with patch('xapi.xapi_tracker.XapiBackend.get_context') as get_context:
            get_context.return_value = {}
            call_command('send_offline_data_2_tincan', *args, **opts)
            self.assertEqual(TrackingLog.objects.count(), 1)

            print "# Recall to check same event not added anymore"
            call_command('send_offline_data_2_tincan', *args, **opts)
            self.assertEqual(TrackingLog.objects.count(), 1)


@override_settings(TRACKING_BACKENDS=XAPI_BACKEND_SETTINGS)
class XapiSend2TincanTest(XapiTest):
    def setUp(self):
        super(XapiSend2TincanTest, self).setUp()

    @unittest.skipUnless(
        os.environ.get('XAPI_URL_LRS') != '',
        "#### Test data_2_tincan need a real LRS API URL#####"
    )
    def test_data_2_tincan(self):
        args = []
        opts = {}
        obj = Activity(
            id=self.backend.base_url + "TEST_EVENT_ID",
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': self.backend.oai_prefix + COURSE_ID}),
                type="http://adlnet.gov/expapi/activities/course"
            )
        )
        verb = LearnerAccessesMoocVerb.get_verb()
        timestamp = datetime(2012, 1, 1, tzinfo=UTC).isoformat()
        course_parent = {
            "id":  self.backend.oai_prefix + COURSE_ID,
            "objectType": "Activity",
            "definition": {
                "name": {
                    "en-US": "COURSE_TEST"
                },
                "description": {
                    "en-US": "TESTING"
                },
                "type": "http://adlnet.gov/expapi/activities/course"
            }
        }
        parents = []
        parents.append(course_parent)

        context = {
            "contextActivities": {
                "parent": parents
            }
        }
        actor = {
            "objectType": "Agent",
            "account": {
                "homePage": "%s?user=%s" % (TEST_HOMEPAGE_URL, TEST_UID),
                "name": TEST_UID
            }
        }
        statement = {
            'actor': actor,
            'verb': verb.to_json(),
            'object': obj.to_json(),
            'timestamp': timestamp,
            'context': context
        }

        statement = json.dumps(statement)
        tldat = TrackingLog(
            dtcreated=timestamp,
            user_id=1,
            course_id=COURSE_ID,
            statement=statement
        ).save()
        call_command('send_data_2_tincan', *args, **opts)
        tldat = TrackingLog.objects.all()[:1].get()
        self.assertTrue(tldat.exported)
        self.assertIsNotNone(tldat.tincan_key)
        self.assertEqual(json.loads(tldat.tincan_key)['result'].lower(), "ok")


@ddt  # pylint: disable=too-many-ancestors
class TinCanRuleTest(XapiTest):

    def setUp(self):
        super(TinCanRuleTest, self).setUp()
        raw_data = open(TEST_FILE_TRACKING).read()
        lines = [l.strip() for l in raw_data.split('\n') if l.strip() != '']
        self.basic_event = json.loads(lines[0])
        self.course_id = SPLIT_COURSE_ID

    def base_rule_test(self, rule, basic_event, course_id):
        is_matched = rule.match(basic_event, course_id)
        self.assertTrue(is_matched)
        verb, obj = rule.convert(basic_event, course_id)
        self.assertIsNotNone(verb)
        self.assertIsNotNone(obj)

    @data(
        "/courses/"+SPLIT_COURSE_ID+"/info",
        "/courses/"+COURSE_ID+"/info",
        "/courses/"+SPLIT_COURSE_ID+"/about",
        "/courses/"+COURSE_ID+"/about"
    )
    def test_access_course(self, event_type):
        self.basic_event["event_type"] = event_type
        rule = AccessCourseRule()
        self.base_rule_test(rule, self.basic_event, self.course_id)

    @data(
        "/courses/"+SPLIT_COURSE_ID+"/courseware/122324",
        "/courses/"+COURSE_ID+"/courseware/122324",
        "/courses/"+SPLIT_COURSE_ID+"/courseware/",
        "/courses/"+COURSE_ID+"/courseware/"
    )
    def test_access_module(self, event_type):
        self.basic_event["event_type"] = event_type
        rule = AccessModuleRule()
        self.base_rule_test(rule, self.basic_event, self.course_id)

    @patch('xapi.utils.get_course_title')
    def test_enrollment(self, mock_get_course_title):
        mock_get_course_title.return_value = "COURSE_TITLE"
        self.basic_event["event_source"] = "server"
        self.basic_event["event_type"] = "edx.course.enrollment.activated"
        rule = LearnerEnrollMOOCRule()
        self.base_rule_test(rule, self.basic_event, self.course_id)
        self.basic_event["event_type"] = "edx.course.enrollment.deactivated"
        rule = LearnerUnEnrollMOOCRule()
        self.base_rule_test(rule, self.basic_event, self.course_id)

    @data(
        "/courses/"+SPLIT_COURSE_ID+"/wiki/_create/***",
        "/courses/"+COURSE_ID+"/wiki/_create/",
        "/courses/"+SPLIT_COURSE_ID+"/wiki/UpdatePage/_edit/",
        "/courses/"+COURSE_ID+"/wiki/UpdatePage/_edit/",
        "/courses/"+SPLIT_COURSE_ID+"/wiki/APage/",
        "/courses/"+COURSE_ID+"/wiki/APage/",
    )
    def test_wiki(self, event_type):
        self.basic_event["event_type"] = event_type
        event = {"POST": {"title": ["WIKI_TITLE"]}}
        self.basic_event["event"] = event
        tincan = self.backend.tincan
        tincan.patterns = [
            x for x in self.backend.tincan.patterns
            if (
                isinstance(x, AccessWikiRule) or
                isinstance(x, AccessWikiPageRule) or
                isinstance(x, CreateWikiRule) or
                isinstance(x, EditWikiRule)
            )
        ]
        verb, obj = tincan.to_xapi(self.basic_event, self.course_id)
        self.assertIsNotNone(verb)
        self.assertIsNotNone(obj)

    @data(
        "/courses/"+SPLIT_COURSE_ID,
        "/courses/"+COURSE_ID
    )
    def test_access_problem(self, baseeventtype):
        event_type = baseeventtype
        event_type += "/xblock/block-v1:edx+Demo+demo+type@problem+block@__27"
        event_type += "/handler/xmodule_handler/problem_get"
        self.basic_event["event_type"] = event_type
        self.basic_event["event_source"] = "server"
        rule = AccessProblemRule()
        self.base_rule_test(rule, self.basic_event, self.course_id)

    def test_problem_check(self):
        self.basic_event["event_type"] = "problem_check"
        self.basic_event["event_source"] = "server"
        event = {"problem_id": "PROBLEM_ID"}
        context = {"module": {"display_name": "Quiz 1"}}
        self.basic_event["event"] = event
        self.basic_event["context"] = context
        rule = ProblemCheckRule()
        self.base_rule_test(rule, self.basic_event, self.course_id)

    @data(
        "play_video",
        "load_video"
    )
    def test_video(self, event_type):
        self.basic_event["event_type"] = event_type
        self.basic_event["event_source"] = "browser"
        event = {"id": "VIDEO_ID"}
        self.basic_event["event"] = event
        tincan = self.backend.tincan
        tincan.patterns = [
            x for x in self.backend.tincan.patterns
            if (
                isinstance(x, LoadVideoRule) or
                isinstance(x, PlayVideoRule)
            )
        ]
        verb, obj = tincan.to_xapi(self.basic_event, self.course_id)
        self.assertIsNotNone(verb)
        self.assertIsNotNone(obj)

    @data(
        "edx.forum.thread.created",
        "edx.forum.response.created",
        "/courses/"+SPLIT_COURSE_ID+"/discussion/comments/56334b88424072495b000001/upvote",
        "/courses/"+COURSE_ID+"/discussion/comments/56334b88424072495b000001/upvote",
        "/courses/"+SPLIT_COURSE_ID+"/discussion/threads/56334b88424072495b000001/upvote",
        "/courses/"+COURSE_ID+"/discussion/threads/56334b88424072495b000001/upvote",
        "/courses/"+SPLIT_COURSE_ID+"/discussion/forum/an-i4x-string/threads/56334b88424072495b000001",
        "/courses/"+COURSE_ID+"/discussion/forum/an-i4x-string/threads/56334b88424072495b000001",
        "/courses/"+SPLIT_COURSE_ID+"/discussion/forum",
        "/courses/"+COURSE_ID+"/discussion/forum",
    )
    def test_forum(self, event_type):
        self.basic_event["event_type"] = event_type
        self.basic_event["referer"] = "REFERER"
        event = {"title": "TITLE_MESSAGE"}
        self.basic_event["event"] = event
        context = {"path": "PATH"}
        self.basic_event["context"] = context
        tincan = self.backend.tincan
        tincan.patterns = [
            x for x in self.backend.tincan.patterns
            if (
                isinstance(x, ForumAccessRule) or
                isinstance(x, ForumCreateThreadRule) or
                isinstance(x, ForumLikesRule) or
                isinstance(x, ForumReadsRule) or
                isinstance(x, ForumReplyRule)
            )
        ]
        verb, obj = tincan.to_xapi(self.basic_event, self.course_id)
        self.assertIsNotNone(verb)
        self.assertIsNotNone(obj)

    @data(
        "/courses/"+SPLIT_COURSE_ID+"/xblock/XBLOCK_KEY_@+:/handler/render_peer_assessment",
        "/courses/"+COURSE_ID+"/xblock/XBLOCK_KEY_@+:/handler/render_peer_assessment",
        "/courses/"+SPLIT_COURSE_ID+"/xblock/XBLOCK_KEY_@+:/handler/submit",
        "/courses/"+COURSE_ID+"/xblock/XBLOCK_KEY_@+:/handler/submit",
        "/courses/"+SPLIT_COURSE_ID+"/xblock/XBLOCK_KEY_@+:/handler/peer_assess",
        "/courses/"+COURSE_ID+"/xblock/XBLOCK_KEY_@+:/handler/peer_assess",
        "/courses/"+SPLIT_COURSE_ID+"/xblock/XBLOCK_KEY_@+:/handler/self_assess",
        "/courses/"+COURSE_ID+"/xblock/XBLOCK_KEY_@+:/handler/self_assess",

    )
    def test_peer(self, event_type):
        self.basic_event["event_type"] = event_type
        context = {"path": "PATH"}
        self.basic_event["context"] = context
        tincan = self.backend.tincan
        tincan.patterns = [
            x for x in self.backend.tincan.patterns
            if (
                isinstance(x, AccessPeerAssessmentRule) or
                isinstance(x, SubmitsPeerAssessmentRule) or
                isinstance(x, SubmitsPeerFeedbackRule) or
                isinstance(x, SubmitsSelfFeedbackRule)
            )
        ]
        verb, obj = tincan.to_xapi(self.basic_event, self.course_id)
        self.assertIsNotNone(verb)
        self.assertIsNotNone(obj)
