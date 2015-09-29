"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os
from django.test import TestCase
from django.test.utils import override_settings
from django.core.management import call_command
from social.apps.django_app.default.models import UserSocialAuth

from student.tests.factories import UserFactory

from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from eventtracking import tracker
from eventtracking.django import DjangoTracker
from xapi.xapi_tracker import XapiBackend
from xapi.models import TrackingLog

TEST_UID = "test_social_uid"
TEST_HOMEPAGE_URL = "localhost"
TEST_USERNAME = "test-actor"
TEST_FILE_TRACKING = os.getcwd()+"/xapi/test_data/tracking.log"
TEST_BACKEND_OPTIONS = {
    "name": "xapi",
    "ID_COURSES": ['course-v1:ORG+COURSE+RUN', 'ORG/COURSE/RUN'],  # list of course_id you want to track on LRS
    "USERNAME_LRS": "",  # username for the LRS endpoint
    "PASSWORD_LRS": "",  # password for the LRS endpoint
    "URL": "http://mylrs.endpoint/xAPI/statements",  # the LRS endpoint API URL
    "EXTRACTED_EVENT_NUMBER": 100,  # number of batch statements to extract from db and     sent in a job
    "HOMEPAGE_URL": TEST_HOMEPAGE_URL
}


class XapiTest(ModuleStoreTestCase):

    @override_settings(FEATURES={'ENABLE_THIRD_PARTY_AUTH': True})
    def setUp(self):
        super(XapiTest, self).setUp()
        self.tracker = DjangoTracker()
        tracker.register_tracker(self.tracker)
        course1 = CourseFactory.create(
            org="ORG", course="COURSE", display_name="RUN", default_store=ModuleStoreEnum.Type.mongo
        )
        course2 = CourseFactory.create(
            org="ORG", course="COURSE", display_name="RUN", default_store=ModuleStoreEnum.Type.split
        )
        print "######### COURSE2 CREATE " + course2.id
        print "######### COURSE CREATE " + course.id
        user = UserFactory.create(username=TEST_USERNAME)
        UserSocialAuth.objects.create(user=user, provider="eco", uid=TEST_UID)
        self.user = user
        options = TEST_BACKEND_OPTIONS
        self.backend = XapiBackend(**options)

    def test_send_offline(self):

        print os.getcwd()
        args = []
        opts = {"filename": TEST_FILE_TRACKING, "course_ids": (",").join(TEST_BACKEND_OPTIONS.get("ID_COURSES"))}
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
