from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.eco_verbs import LearnerEnrollMoocVerb, LearnerUnenrollMoocVerb
import xapi.utils as xutils


class BaseEnrollRule(BasePattern):  # pylint: disable=abstract-method

    def convert(self, evt, course_id):
        verb = self.get_verb()  # pylint: disable=no-member
        title = xutils.get_course_title(course_id)
        obj = Activity(
            id=self.oai_prefix + course_id,
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': title}),
                type="http://adlnet.gov/expapi/activities/course"
            )
        )
        return verb, obj


class LearnerEnrollMOOCRule(BaseEnrollRule, LearnerEnrollMoocVerb):

    def match(self, evt, course_id):
        return (evt['event_type'] == 'edx.course.enrollment.activated' and
                evt['event_source'] == 'server')


class LearnerUnEnrollMOOCRule(BaseEnrollRule, LearnerUnenrollMoocVerb):

    def match(self, evt, course_id):
        return (evt['event_type'] == 'edx.course.enrollment.deactivated' and
                evt['event_source'] == 'server')
