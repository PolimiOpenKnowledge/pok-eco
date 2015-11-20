import re

from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.eco_verbs import LearnerAccessesMoocVerb


# Learner accesses MOOC
class AccessCourseRule(BasePattern, LearnerAccessesMoocVerb):
    def match(self, evt, course_id):
        return (re.match('^/courses/.*/info/?', evt['event_type']) or
                re.match('^/courses/.*/about/?', evt['event_type']))

    def convert(self, evt, course_id):
        verb = self.get_verb()
        obj = Activity(
            id=self.fix_id(self.base_url, evt['event_type']),
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': self.oai_prefix + course_id}),
                type="http://adlnet.gov/expapi/activities/course"
            )
        )
        return verb, obj
