# pylint: disable=too-many-arguments

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os
import json
from datetime import datetime
from urlparse import urlparse
from ddt import ddt, data
from pytz import UTC
from mock import patch
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import unittest
from django.core.management import call_command

from eventtracking import tracker
from eventtracking.django import DjangoTracker
from social.apps.django_app.default.models import UserSocialAuth
from tincan import (
    Activity,
    ActivityDefinition,
    Agent,
    AgentAccount,
    Context,
    ContextActivities,
    Extensions,
    LanguageMap
)

from courseware.tests.helpers import get_request_for_user
from student.tests.factories import UserFactory

from xapi.xapi_tracker import XapiBackend
from xapi.tincan_wrapper import TinCanWrapper
from xapi.models import TrackingLog, XapiBackendConfig
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
from xapi.patterns.eco_verbs import LearnerAccessesMoocVerb


SPLIT_COURSE_ID = "course-v1:ORG+COURSE+RUN"
COURSE_ID = 'ORG/COURSE/RUN'
TEST_UID = "test_social_uid"
TEST_HOMEPAGE_URL = "https://portal.ecolearning.eu"
TEST_USERNAME = "test-actor"
TEST_FILE_TRACKING = os.getcwd()+"/xapi/test_data/tracking.log"
TEST_FILE_TRACKING_OFFLINE = os.getcwd()+"/xapi/test_data/tracking_offline.log"
OAI_PREFIX = 'oai:it.polimi.pok:'
XAPI_BACKEND_CONFIG = {
    "id_courses": SPLIT_COURSE_ID + "," + COURSE_ID,
    "username_lrs": os.environ.get('XAPI_USERNAME_LRS', ""),  # username for the LRS endpoint
    "password_lrs": os.environ.get('XAPI_PASSWORD_LRS', ""),  # password for the LRS endpoint
    "lrs_api_url": os.environ.get('XAPI_URL_LRS', ""),  # the LRS endpoint API URL
    "extracted_event_number": 100,  # number of batch statements to extract from db and     sent in a job
    "user_profile_home_url": TEST_HOMEPAGE_URL,
    "base_url": "https://www.pok.polimi.it/",
    "oai_prefix": OAI_PREFIX,
    "enabled": True
}
XAPI_BACKEND_SETTINGS = {
    'xapi': {
        'ENGINE': 'xapi.xapi_tracker.XapiBackend',
        'OPTIONS': {
            "name": "xapi",
        }
    }
}
OPENASSESSMENT_KEY = "block-v1:edx+Demo+demo:1+2+3+type@openassessment+block@Name"
TIME_MILLIS = "2015-09-25T15:27:05.152330+00:00"


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
        fields = dict(XAPI_BACKEND_CONFIG)
        XapiBackendConfig(**fields).save()
        self.backend = XapiBackend()
        self.tincanwrapper = TinCanWrapper()

    def test_get_actor(self):

        expected_actor = Agent(
            account=AgentAccount(
                home_page="%s?user=%s" % (TEST_HOMEPAGE_URL, TEST_UID),
                name=TEST_UID
            )
        )

        actor = self.backend.get_actor(self.user.id)
        self.assertIsNotNone(actor)
        self.assertEqual(expected_actor, actor)


class XapiSendOfflineTest(XapiTest):
    def setUp(self):
        super(XapiSendOfflineTest, self).setUp()

    def test_send_offline(self):
        args = []
        opts = {"filename": TEST_FILE_TRACKING_OFFLINE}
        with patch('xapi.xapi_tracker.XapiBackend.get_context') as get_context:
            parents = []
            course_parent = Activity(
                id=OAI_PREFIX + COURSE_ID,
                definition=ActivityDefinition(
                    name=LanguageMap({'en-US': "title"}),
                    description=LanguageMap({'en-US': "description"}),
                    type="http://adlnet.gov/expapi/activities/course"
                )
            )
            parents.append(course_parent)
            context = Context(
                contextActivities=ContextActivities(
                    parent=parents
                ),
                extensions=Extensions({"time_with_millis": TIME_MILLIS})
            )
            get_context.return_value = context
            call_command('send_offline_data_2_tincan', *args, **opts)
            self.assertEqual(TrackingLog.objects.count(), 1)

            print "# Recall to check same event not added anymore"
            call_command('send_offline_data_2_tincan', *args, **opts)
            self.assertEqual(TrackingLog.objects.count(), 1)


class XapiSend2TincanTest(XapiTest):
    def setUp(self):
        super(XapiSend2TincanTest, self).setUp()

    @unittest.skipUnless(
        os.environ.get('XAPI_URL_LRS', '') != '',
        "#### Test data_2_tincan need a real LRS API URL#####"
    )
    @override_settings(TRACKING_BACKENDS=XAPI_BACKEND_SETTINGS)
    def test_data_2_tincan(self):
        args = []
        opts = {}
        obj = Activity(
            id="block-v1:Polimi+FIS101+2015_M9+type@video+block@W1M1L1_video",
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': OAI_PREFIX + COURSE_ID}),
                type="http://adlnet.gov/expapi/activities/course"
            )
        )
        verb = LearnerAccessesMoocVerb.get_verb()
        timestamp = datetime(2012, 1, 1, tzinfo=UTC).isoformat()
        course_parent = {
            "id":  OAI_PREFIX + COURSE_ID,
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

        tldat = TrackingLog(
            dtcreated=timestamp,
            user_id=1,
            course_id=COURSE_ID,
            statement=json.dumps(statement)
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

    def base_rule_test(self, rule, basic_event, course_id, expected_obj_id):
        is_matched = rule.match(basic_event, course_id)
        self.assertTrue(is_matched)
        verb, obj = rule.convert(basic_event, course_id)
        self.assertIsNotNone(verb)
        self.assertIsNotNone(obj)
        self.assertTrue(self.isURI(obj.id))
        if expected_obj_id:
            self.assertEqual(obj.id, expected_obj_id)

    @staticmethod
    def isURI(url):
        '''
        Basic URI validation for edx
        '''
        par = urlparse(url)
        validURI = par.scheme != '' and (par.netloc != '' or par.path != '')
        if not validURI:
            print par
        return validURI

    @data(
        "/courses/"+SPLIT_COURSE_ID+"/info",
        "/courses/"+COURSE_ID+"/info",
        "/courses/"+SPLIT_COURSE_ID+"/about",
        "/courses/"+COURSE_ID+"/about"
    )
    def test_access_course(self, event_type):
        self.basic_event["event_type"] = event_type
        expected_object_id = OAI_PREFIX + self.course_id
        rule = AccessCourseRule()
        self.base_rule_test(rule, self.basic_event, self.course_id, expected_object_id)

    @data(
        "/courses/"+SPLIT_COURSE_ID+"/courseware/abibo/122324",
        "/courses/"+COURSE_ID+"/courseware/abibo/122324",
        "/courses/"+SPLIT_COURSE_ID+"/courseware/",
        "/courses/"+COURSE_ID+"/courseware/"
    )
    @patch('xapi.patterns.AccessModuleRule.get_block_id')
    def test_access_module(self, event_type, mock_get_usage_key):
        mock_get_usage_key.return_value = "block-v1:ORG+TEST101+RUNCODE+type@sequential+block@122324"
        self.basic_event["event_type"] = event_type
        rule = AccessModuleRule()
        self.base_rule_test(rule, self.basic_event, self.course_id, mock_get_usage_key.return_value)

    @patch('xapi.utils.get_course_title')
    def test_enrollment(self, mock_get_course_title):
        mock_get_course_title.return_value = "COURSE_TITLE"
        expected_object_id = OAI_PREFIX + self.course_id
        self.basic_event["event_source"] = "server"
        self.basic_event["event_type"] = "edx.course.enrollment.activated"
        ruleEnroll = LearnerEnrollMOOCRule()
        self.base_rule_test(ruleEnroll, self.basic_event, self.course_id, expected_object_id)
        self.basic_event["event_type"] = "edx.course.enrollment.deactivated"
        ruleUnenroll = LearnerUnEnrollMOOCRule()
        self.base_rule_test(ruleUnenroll, self.basic_event, self.course_id, expected_object_id)

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
        expected_object_id = "block-v1:edx+Demo+demo+type@problem+block@__27"
        event_type = baseeventtype
        event_type += "/xblock/"+expected_object_id
        event_type += "/handler/xmodule_handler/problem_get"
        self.basic_event["event_type"] = event_type
        self.basic_event["event_source"] = "server"
        rule = AccessProblemRule()
        self.base_rule_test(rule, self.basic_event, self.course_id, expected_object_id)

    def test_problem_check(self):
        self.basic_event["event_type"] = "problem_check"
        self.basic_event["event_source"] = "server"
        expected_object_id = "block-v1:edx+Demo+demo+type@problem+block@W1M2Q1_001"
        event = {"problem_id": expected_object_id}
        context = {"module": {"display_name": "Quiz 1"}}
        self.basic_event["event"] = event
        self.basic_event["context"] = context
        rule = ProblemCheckRule()
        self.base_rule_test(rule, self.basic_event, self.course_id, expected_object_id)

    @data(
        "play_video",
        "load_video"
    )
    @patch('xapi.patterns.LoadVideoRule.get_block_id')
    @patch('xapi.patterns.PlayVideoRule.get_block_id')
    def test_video(self, event_type, load_get_object_id, play_get_object_id):
        expected_object_id = "block-v1:+"+self.course_id+"+type@video+block@VIDEO_ID"
        load_get_object_id.return_value = expected_object_id
        play_get_object_id.return_value = expected_object_id
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
        self.assertTrue(self.isURI(obj.id))
        self.assertEqual(obj.id, expected_object_id)

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
        "/courses/"+SPLIT_COURSE_ID+"/xblock/"+OPENASSESSMENT_KEY+"/handler/render_peer_assessment",
        "/courses/"+COURSE_ID+"/xblock/"+OPENASSESSMENT_KEY+"/handler/render_peer_assessment",
        "/courses/"+SPLIT_COURSE_ID+"/xblock/"+OPENASSESSMENT_KEY+"/handler/submit",
        "/courses/"+COURSE_ID+"/xblock/"+OPENASSESSMENT_KEY+"/handler/submit",
        "/courses/"+SPLIT_COURSE_ID+"/xblock/"+OPENASSESSMENT_KEY+"/handler/peer_assess",
        "/courses/"+COURSE_ID+"/xblock/"+OPENASSESSMENT_KEY+"/handler/peer_assess",
        "/courses/"+SPLIT_COURSE_ID+"/xblock/"+OPENASSESSMENT_KEY+"/handler/self_assess",
        "/courses/"+COURSE_ID+"/xblock/"+OPENASSESSMENT_KEY+"/handler/self_assess",

    )
    @patch('xapi.patterns.AccessPeerAssessmentRule.get_object_id')
    @patch('xapi.patterns.SubmitsPeerAssessmentRule.get_object_id')
    @patch('xapi.patterns.SubmitsPeerFeedbackRule.get_object_id')
    @patch('xapi.patterns.SubmitsSelfFeedbackRule.get_object_id')
    def test_peer(self, event_type, a, b, c, d):
        expected_object_id = OPENASSESSMENT_KEY
        a.return_value = expected_object_id
        b.return_value = expected_object_id
        c.return_value = expected_object_id
        d.return_value = expected_object_id
        self.basic_event["event_type"] = event_type
        context = {"path": event_type}
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
        self.assertTrue(self.isURI(obj.id))
        self.assertEqual(obj.id, expected_object_id)
