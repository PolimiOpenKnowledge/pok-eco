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
import re

from django.db import models

from track.backends import BaseBackend
from xmodule_django.models import CourseKeyField

from social.apps.django_app.default.models import UserSocialAuth
from courseware.courses import get_course_by_id, get_course_about_section
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from opaque_keys.edx.locations import SlashSeparatedCourseKey


# TODO: è giusto? era così:
# log = logging.getLogger('track.backends.django')
log = logging.getLogger('xapi.xapi_tracker')


LOGFIELDS = [
    'user_id',
    'course_id',
    'statement',
]

ACCESS_VERB = {
    "id": "http://activitystrea.ms/schema/1.0/access",
    "display": {"en-US": "Indicates the learner accessed something"}
}
SUBMIT_VERB = {
    "id": "http://activitystrea.ms/schema/1.0/submit",
    "display": {"en-US": "Indicates the learner submitted something"}
}
REGISTERED_VERB = {
    "id": "http://adlnet.gov/expapi/verbs/registered",
    "display": {"en-US": "Indicates the learner registered/enrolled for MOOC"}
}
EXITED_VERB = {
    "id": "http://adlnet.gov/expapi/verbs/exited",
    "display": {"en-US": "Indicates the learner leaves the MOOC"}
}
EDX2TINCAN = {
    'learner_accesses_MOOC': ACCESS_VERB,
    'learner_accesses_a_module': ACCESS_VERB,
    'learner_enroll_MOOC': REGISTERED_VERB,
    'learner_unenroll_MOOC': EXITED_VERB,

    # ################ ASSESSMENT ################################
    'learner_accesses_assessment': ACCESS_VERB,
    'learner_answers_question': {
        "id": "http://adlnet.gov/expapi/verbs/answered",
        "display": {"en-US": "Indicates the learner answered a question"}
    },

    # ################ PEER ASSESSMENT ###########################
    'learner_accesses_peer_assessment': ACCESS_VERB,
    'learner_submits_assessment': SUBMIT_VERB,
    'learner_submits_peer_feedback': SUBMIT_VERB,
    'learner_submits_peer_product': SUBMIT_VERB,

    # ################ FORUM #####################################
    'learner_accesses_forum': ACCESS_VERB,
    'learner_post_new_forum_thread': {
        "id": "http://activitystrea.ms/schema/1.0/author",
        "display": {"en-US": "Indicates the learner authored something"}
    },
    'learner_replies_to_forum_message': {
        "id": "http://adlnet.gov/expapi/verbs/commented",
        "display": {"en-US": "Indicates the learner commented on something"}
    },
    'learner_liked_forum_message': {
        "id": "http://activitystrea.ms/schema/1.0/like",
        "display": {"en-US": "Indicates the learner liked a forum message"}
    },
    'learner_reads_forum_message': {
        "id": "http://activitystrea.ms/schema/1.0/read",
        "display": {"en-US": "Indicates the learner read a forum message"}
    },

    # ################ ASSIGNMENT #################################
    # NOT USED 'learner_accesses_assignment': ACCESS_VERB,
    # NOT USED 'learner_submit_assignment': ACCESS_VERB,

    # ################ WIKI #######################################
    'learner_accesses_wiki': ACCESS_VERB,
    'learner_accesses_wiki_page': ACCESS_VERB,
    'learner_creates_wiki_page': {
        "id": "http://activitystrea.ms/schema/1.0/create",
        "display": {"en-US": "Indicates the learner created something"}
    },
    'learner_edits_wiki_page': {
        "id": "http://activitystrea.ms/schema/1.0/update",
        "display": {"en-US": "Indicates the learner updated or edited something"}
    },
    # ################ VIDEO ######################################
    'load_video': ACCESS_VERB,
    'play_video': {
        "id": "http://activitystrea.ms/schema/1.0/watch",
        "display": {"en-US": "Indicates the learner has watched video xyz"}
    }
}


def get_course(course_id):
    course_key = ""
    try:
        course_key = CourseKey.from_string(course_id)
    except InvalidKeyError:
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    course = get_course_by_id(course_key)
    return course


class TrackingLog(models.Model):
    """This model defines the fields that are stored in the tracking log database."""

    dtcreated = models.DateTimeField('creation date')
    user_id = models.IntegerField(blank=True)
    course_id = CourseKeyField(max_length=255, blank=True)
    statement = models.TextField(blank=True)
    tincan_key = models.CharField(max_length=512, null=True, blank=True)
    tincan_error = models.TextField(blank=True, null=True, default='')
    exported = models.BooleanField(default=False)

    class Meta(object):
        app_label = 'xapi'
        db_table = 'xapi_trackinglog'

    def __unicode__(self):
        fmt = (
            u"[{self.dtcreated}] {self.user_id}@{self.course_id}: "
        )
        return fmt.format(self=self)  # pylint: disable=redundant-keyword-arg


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

        self.course_ids = set(options.get('ID_COURSES', []))
        """
        TEST_COURSES = [
                'Polimi/GestConf101/2014_T1', 'course-v1:Polimi+FIS102+2014_M11', 'course-v1:Polimi+FIS102+2015',
                'course-v1:Polimi+MAT101+2015', 'course-v1:Polimi+FIS101+2014_M12', 'Polimi/MAT101/2014_T2',
                'Polimi/FinAccount101/2014_T2', 'course-v1%3APolimi%2BMAT101%2B2015_M4/courseware/WF',
                'course-v1:Polimi+FinAccount101+2015_M1', 'course-v1%3APolimi%2BMAT101%2B2015_M4/courseware/W3',
                'course-v1%3APolimi%2BFIS102%2B2015_M4/courseware/W2',
                'course-v1:Polimi+FIS101+2014_M11', 'course-v1:Polimi+GestCamb101+2015_M4',
                'course-v1:Polimi+FIS101+2015', 'course-v1:Polimi+FIS102+2014_M12',
                'course-v1:Polimi+GestConf101+2015_M4', 'course-v1:Polimi+GestConf101+2014_M12',
                'course-v1:Polimi+MAT101+2014_M11', 'course-v1:Polimi+MAT101+2014_M12',
                'course-v1:Polimi+MAT101+2015_M2', 'course-v1:Polimi+MAT101+2015_M4', 'course-v1:Polimi+FIS101+2015_M2',
                'course-v1:Polimi+FIS101+2015_M4', 'course-v1:Polimi+FIS102+2015_M4',
                'course-v1:Polimi+MANCHAN101+2015_M4', 'course-v1:Polimi+FinAccount101+2015_M6',
                'course-v1:Polimi+FinAccount101+2015_M6', 'course-v1:polimi+finaccount101+2015_m4',
                'course-v1:Polimi+FinAccount101+2015_M4', 'Polimi/FIS101/2014_T2',
                'course-v1:Polimi+GestConf101+2015_M2'
        ]
        for c in TEST_COURSES:
            self.course_ids.add(c)
        """
        self.base_url = options.get('BASE_URL', 'https://www.pok.polimi.it/')
        self.homepage_url = options.get('HOMEPAGE_URL', 'https://portal.ecolearning.eu')
        self.oai_prefix = options.get('OAI_PREFIX', 'oai:it.polimi.pok:')
        self.name = name

    # See https://github.com/adlnet/edx-xapi-bridge/blob/master/xapi-bridge/converter.py
    def to_xapi(self, evt, course_id):
        def fix_id(base_url, obj_id):
            if not obj_id.startswith("https"):
                return base_url + obj_id
            return obj_id

        # evt['time'] = evt['time'].strftime("%Y-%m-%dT%H:%M:%S")
        # return evt
        action = {}
        obj = {}
        if re.match('^/courses/.*/info/?', evt['event_type']) or re.match('^/courses/.*/about/?', evt['event_type']):
            # Learner accesses MOOC
            action = EDX2TINCAN['learner_accesses_MOOC']
            obj = {
                "objectType": "Activity",
                "id": fix_id(self.base_url, evt['event_type']),
                "definition": {
                    "name": {"en-US": self.oai_prefix + course_id},
                    "type": "http://adlnet.gov/expapi/activities/course"
                }
            }

        # /courses/course-v1:Polimi+GestConf101+2015_M4/courseware
        # elif evt['event_type'] ==
        #           u'/courses/edX/DemoX/Demo_Course/courseware/d8a6192ade314473a78242dfeedfbf5b/edx_introduction/':
        elif re.match('^/courses/.*/courseware/?\w*', evt['event_type']):
            action = EDX2TINCAN['learner_accesses_a_module']
            module = evt['event_type'].split('/')[-2:][0]
            obj = {
                "objectType": "Activity",
                "id": fix_id(self.base_url, evt['context']['path']),
                "definition": {
                    "name": {"en-US": module},
                    "type": "http://adlnet.gov/expapi/activities/module"
                }
            }
        elif evt['event_type'] == 'edx.course.enrollment.activated' and evt['event_source'] == 'server':
            action = EDX2TINCAN['learner_enroll_MOOC']
            course = get_course(course_id)
            title = get_course_about_section(course, "title")
            obj = {
                "objectType": "Activity",
                "id":  self.oai_prefix + course_id,
                "definition": {
                    "name": {"en-US": title},
                    "type": "http://adlnet.gov/expapi/activities/course"
                }
            }
        elif evt['event_type'] == 'edx.course.enrollment.deactivated' and evt['event_source'] == 'server':
            action = EDX2TINCAN['learner_unenroll_MOOC']
            course = get_course(course_id)
            title = get_course_about_section(course, "title")
            obj = {
                "objectType": "Activity",
                "id":  self.oai_prefix + course_id,
                "definition": {
                    "name": {"en-US": title},
                    "type": "http://adlnet.gov/expapi/activities/course"
                }
            }
        elif re.match('/courses[/\w]+/wiki/\w+/_create/?', evt['event_type']):
            title = None
            try:
                # We need to do this because we receive a string instead than a dictionary
                event_data = json.loads(evt['event'])
                title = event_data['POST'].get('title', None)
            except:
                pass
            if title:
                action = EDX2TINCAN['learner_creates_wiki_page']
                obj = {
                    "objectType": "Activity",
                    "id": fix_id(self.base_url, evt['context']['path']),
                    "definition": {
                        "name": {"en-US": title},
                        "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                    }
                }
            else:
                action = None  # Skip the not really created pages
        elif re.match('/courses[/\w]+/wiki[/\w]+/_edit/?', evt['event_type']):
            # EX: /courses/edX/DemoX/Demo_Course/wiki/DemoX/_edit/ or
            #     /courses/edX/DemoX/Demo_Course/wiki/DemoX/page/_edit/
            title = None
            try:
                # We need to do this because we receive a string instead than a dictionary
                event_data = json.loads(evt['event'])
                title = event_data['POST'].get('title', None)
            except:
                pass
            if title:
                action = EDX2TINCAN['learner_edits_wiki_page']
                obj = {
                    "objectType": "Activity",
                    "id": fix_id(self.base_url, evt['context']['path']),
                    "definition": {
                        "name": {"en-US": title},
                        "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                    }
                }
            else:
                action = None  # Skip the not really edited pages

        elif re.match('/courses[/\w]+/wiki/\w+/\w+/?', evt['event_type']):
            action = EDX2TINCAN['learner_accesses_wiki_page']
            obj = {
                "objectType": "Activity",
                "id": fix_id(self.base_url, evt['context']['path']),
                "definition": {
                    "name": {"en-US": evt['context']['path']},
                    "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                }
            }
        elif re.match('/courses[/\w]+/wiki/\w+/?', evt['event_type']):
            action = EDX2TINCAN['learner_accesses_wiki']
            obj = {
                "objectType": "Activity",
                "id": fix_id(self.base_url, evt['context']['path']),
                "definition": {
                    "name": {"en-US": evt['context']['path']},
                    "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                }
            }

        # ########################## ASSESSMENT ################################################
        elif re.match('^/courses/[/:;_\w]+/problem_get/?', evt['event_type']) and evt['event_source'] == 'server':
            action = EDX2TINCAN['learner_accesses_assessment']
            # TODO: cosa ci mettiamo come id? non sembra ci sia nient'altro di utile oltre al path
            # self.path aggiunto per poter risolvere l'errore "id is not a valid IRI in object" ricevuto dall'LRS
            obj = {
                "objectType": "Activity",
                "id": fix_id(self.base_url, evt['context']['path']),
                "definition": {
                    "name": {"en-US": evt['context']['path']},
                    "type": "http://adlnet.gov/expapi/activities/question"
                }
            }
        # We check event_source because this event is registered twice (browser and server)
        elif evt['event_type'] == 'problem_check' and evt['event_source'] == 'server':
            action = EDX2TINCAN['learner_answers_question']
            obj = {
                "objectType": "Activity",
                "id": fix_id(self.base_url, evt['event']['problem_id']),
                "definition": {
                    "name": {"en-US": evt['context']['module']['display_name']},
                    "type": "http://adlnet.gov/expapi/activities/question"
                }
            }
        # TODO; messo perché non vedo quello lato server nei log...
        elif evt['event_type'] == 'problem_check' and evt['event_source'] == 'browser':
            action = EDX2TINCAN['learner_answers_question']
            obj = {
                "objectType": "Activity",
                # "id": fix_id(self.base_url, evt['event']), #['problem_id'],
                "id": fix_id(self.base_url, evt['page']),  # ['problem_id'],
                "definition": {
                    "name": {"en-US": evt['page']},
                    "type": "http://adlnet.gov/expapi/activities/question"
                }
            }
        # ########################## END ASSESSMENT #############################################

        # ########################## VIDEO ######################################################
        elif evt['event_type'] == 'play_video' and evt['event_source'] == 'browser':
            action = EDX2TINCAN['play_video']
            try:
                # We need to do this because we receive a string instead than a dictionary
                event = json.loads(evt['event'])
                obj = {
                    "objectType": "Activity",
                    "id": fix_id(self.base_url, evt['page']),
                    "definition": {
                        "name": {"en-US": event['id']},
                        "type": "http://activitystrea.ms/schema/1.0/video"
                    }
                }
            except:
                action = None  # No event data, just skip
        elif evt['event_type'] == 'load_video' and evt['event_source'] == 'browser':
            action = EDX2TINCAN['load_video']
            try:
                # We need to do this because we receive a string instead than a dictionary
                event = json.loads(evt['event'])
                obj = {
                    "objectType": "Activity",
                    "id": fix_id(self.base_url, evt['page']),
                    "definition": {
                        "name": {"en-US": event['id']},
                        "type": "http://activitystrea.ms/schema/1.0/video"
                    }
                }
            except:
                action = None  # No event data, just skip

        # ########################## END VIDEO ##################################################

        # ########################### FORUM #####################################################

        elif re.match('/courses[/\S]+/discussion/[\S]+/create/?', evt['event_type']):
            # Ex: /courses/Polimi/mat101/2012_01/discussion/i4x-Polimi-MAT101-2015_M2/threads/create
            title = None
            try:
                # We need to do this because we receive a string instead than a dictionary
                event_data = json.loads(evt['event'])
                title = event_data['POST'].get('title', None)
            except:
                pass
            if title:
                if isinstance(title, list):
                    title = title[0]
                action = EDX2TINCAN['learner_post_new_forum_thread']
                obj = {
                    "objectType": "Activity",
                    "id": fix_id(self.base_url, evt['context']['path']),
                    "definition": {
                        "name": {"en-US": title},
                        "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                    }
                }
            else:
                action = None  # Skip the not really created post

        elif re.match('/courses[/\S]+/discussion/[\S]+/reply/?', evt['event_type']):
            # Ex: /courses/Polimi/mat101/2012_01/discussion/i4x-Polimi-MAT101-2015_M2/threads/create
            action = EDX2TINCAN['learner_replies_to_forum_message']
            obj = {
                "objectType": "Activity",
                "id": fix_id(self.base_url, evt['context']['path']),
                "definition": {
                    "name": {"en-US": evt['event_type'].split('reply')[0]},
                    "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                }
            }

        elif re.match('/courses[/\S]+/discussion/[\S]+/upvote/?', evt['event_type']):
            # Ex: /courses/Polimi/mat101/2012_01/discussion/i4x-Polimi-MAT101-2015_M2/threads/create
            action = EDX2TINCAN['learner_liked_forum_message']
            obj = {
                "objectType": "Activity",
                "id": fix_id(self.base_url, evt['context']['path']),
                "definition": {
                    "name": {"en-US": evt['event_type'].split('upvote')[0]},
                    "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                }
            }

        elif re.match('/courses[/\S]+/discussion/[\S]+/threads/[\S]+/?', evt['event_type']):
            # Ex: /courses/{ coursId }/discussion/forum/i4x-Polimi-MAT101-2015_M2/threads/5519ab9656c02c3e9f000005
            action = EDX2TINCAN['learner_reads_forum_message']
            obj = {
                "objectType": "Activity",
                "id": fix_id(self.base_url, evt['context']['path']),
                "definition": {
                    "name": {"en-US": evt['event_type']},
                    "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                }
            }

        elif re.match('/courses[/\S]+/discussion/\w+/?', evt['event_type']):
            # Ex: /courses/{courseId}/discussion/forum
            action = EDX2TINCAN['learner_accesses_forum']
            obj = {
                "objectType": "Activity",
                "id": fix_id(self.base_url, evt['context']['path']),
                "definition": {
                    "name": {"en-US": evt['event_type']},
                    "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                }
            }

        # ######################### END FORUM ###################################################

        # ######################### PEER ASSESSMENT #############################################
        elif re.match('/courses/[\S]+/render_peer_assessment/?', evt['event_type']):
            # Ex: /courses/{courseId}/xblock/{item_id}}/handler/render_peer_assessment
            action = EDX2TINCAN['learner_accesses_peer_assessment']
            obj = {
                "objectType": "Activity",
                "id": fix_id(self.base_url, evt['context']['path']),
                "definition": {
                    "name": {"en-US": evt['event_type'].split('render_peer_assessment')[0]},
                    "type": "http://www.ecolearning.eu/expapi/activitytype/peerassessment"
                }
            }

        elif re.match('/courses/[\S]+/submit/?', evt['event_type']):
            # Ex: /courses/{courseId}/xblock/{item_id}/handler/submit
            action = EDX2TINCAN['learner_submits_assessment']
            obj = {
                "objectType": "Activity",
                "id": fix_id(self.base_url, evt['context']['path']),
                "definition": {
                    "name": {"en-US": evt['event_type'].split('submit')[0]},
                    "type": "http://www.ecolearning.eu/expapi/activitytype/peerassessment"
                }
            }

        elif re.match('/courses/[\S]+/peer_assess/?', evt['event_type']):
            # Ex: /courses/{courseId}/xblock/{item_id}/handler/peer_assess
            action = EDX2TINCAN['learner_submits_peer_feedback']
            obj = {
                "objectType": "Activity",
                "id": fix_id(self.base_url, evt['context']['path']),
                "definition": {
                    "name": {"en-US": evt['event_type'].split('peer_assess')[0]},
                    "type": "http://www.ecolearning.eu/expapi/activitytype/peerassessment"
                }
            }

        elif re.match('/courses/[\S]+/self_assess/?', evt['event_type']):
            # Ex: /courses/{courseId}/xblock/{item_id}/handler/self_assess
            action = EDX2TINCAN['learner_submits_peer_product']
            obj = {
                "objectType": "Activity",
                "id": fix_id(self.base_url, evt['context']['path']),
                "definition": {
                    "name": {"en-US": evt['event_type'].split('self_assess')[0]},
                    "type": "http://www.ecolearning.eu/expapi/activitytype/peerassessment"
                }
            }

        # ######################### END PEER ASSESSMENT #########################################
        # List of not recorded actions
        elif evt['event_type'] == 'stop_video':
            action = None
        elif evt['event_type'] == 'pause_video':
            action = None
        elif evt['event_type'] == 'seek_video':
            action = None
        elif evt['event_type'] == 'speed_change_video':
            action = None
        elif re.search('progress', evt['event_type']):
            action = None
        elif re.search('goto_position', evt['event_type']):
            action = None
        elif evt['event_type'] == 'seq_goto':
            action = None
        elif evt['event_type'] == 'seq_next':
            action = None
        elif evt['event_type'] == 'seq_prev':
            action = None
        elif evt['event_type'] == 'show_transcript':
            action = None
        elif evt['event_type'] == 'page_close':
            action = None
        elif evt['event_type'] == 'save_problem_success':
            action = None
        elif evt['event_type'] == 'hide_transcript':
            action = None
        elif re.search('transcript/translation/en', evt['event_type']):
            action = None
        elif re.search('problem_save', 'save_user_state'):
            action = None
        elif re.search('save_user_state', evt['event_type']):
            action = None
        elif re.search('problem_save', evt['event_type']):
            action = None
        elif re.search('input_ajax', evt['event_type']):
            action = None
        elif re.search('problem_check', evt['event_type']):
            action = None
        elif re.search('problem_show', evt['event_type']):
            action = None
        elif re.search('problem_reset', evt['event_type']):
            action = None
        elif re.search('problem_get', evt['event_type']):
            action = None
        elif re.search('reset_problem', evt['event_type']):
            action = None
        elif re.search('list_instructor_tasks', evt['event_type']):
            action = None
        elif re.search('instructor', evt['event_type']):
            action = None
        elif evt['event_type'] == 'problem_graded':
            action = None
        elif evt['event_type'] == 'showanswer':
            action = None
        elif evt['event_type'] == '/change_enrollment':
            action = None
        elif evt['event_type'] == '/create_account':
            action = None
        elif evt['event_type'] == '/accounts/login':
            action = None
        elif re.search('render_submission', evt['event_type']):
            action = None
        elif re.search('render_student_training', evt['event_type']):
            action = None
        elif re.search('spazio_docenti', evt['event_type']):
            action = None
        elif re.search('render_message', evt['event_type']):
            action = None
        elif re.search('render_grade', evt['event_type']):
            action = None
        elif re.search('render_leaderboard', evt['event_type']):
            action = None
        elif re.search('render_self_assessment', evt['event_type']):
            action = None
        elif re.search('role_plays', evt['event_type']):
            action = None
        elif re.search('jump_to_id', evt['event_type']):
            action = None
        elif re.match('^/courses/.*', evt['event_type']):
            action = None
        else:
            # log.info('-> EVENT NOT MANAGED: ', evt['event_type'])  # Uncomment for debug
            evt['time'] = evt['time'].strftime("%Y-%m-%dT%H:%M:%S")
            action = evt

        return action, obj

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
        course = get_course(course_id)
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
        course_id = event_edx['context'].get('course_id', None)
        if course_id is None or course_id == '':
            try:
                # We need to do this because we receive a string instead than a dictionary
                event = json.loads(event_edx['event'])
                course_id = event['POST'].get('course_id', None)[0]
            except:
                pass  # No event data, just skip
        if course_id in self.course_ids:
            try:
                # Sometimes we receive time as python datetime, sometimes as string...
                try:
                    timestamp = event_edx['time'].isoformat()  # ststrftime("%Y-%m-%dT%H:%M:%S%f%z")
                except AttributeError:
                    timestamp = event_edx['time']

                verb, obj = self.to_xapi(event_edx, course_id)
                actor = self.get_actor(event_edx['context']['user_id'])
                context = self.get_context(course_id)
                # verb = None means to not record the action
                if verb:
                    statement = {
                        'actor': actor,
                        'verb': verb,
                        'object': obj,
                        'timestamp': timestamp,
                        'context': context
                    }

                    statement = json.dumps(statement)

                    tldat = TrackingLog(
                        dtcreated=timestamp,  # event_edx['time'],
                        user_id=event_edx['context']['user_id'],
                        course_id=course_id,
                        statement=statement
                    )

                    # We don't need to add duplication event test, so we save directly
                    tldat.save()

            except Exception as e:  # pylint: disable=broad-except
                log.exception(e)
        else:
            if course_id != '':
                print 'Course not activated', course_id  # Uncomment for debug
                pass
