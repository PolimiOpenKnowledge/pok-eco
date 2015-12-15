from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.eco_verbs import LearnerAccessesAssessmentVerb


class AccessProblemRule(BasePattern, LearnerAccessesAssessmentVerb):

    def match(self, evt, course_id):
        return (evt['event_type'].endswith("problem_get") and
                evt['event_source'] == 'server')

    def convert(self, evt, course_id):
        verb = self.get_verb()
        obj = Activity(
            id=self.get_object_id(evt['event_type']),
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': evt['event_type']}),
                type="http://adlnet.gov/expapi/activities/question"
            )
        )
        return verb, obj
