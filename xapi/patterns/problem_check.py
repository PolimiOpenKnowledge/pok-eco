from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.eco_verbs import LearnerAnswersQuestionVerb


class ProblemCheckRule(BasePattern, LearnerAnswersQuestionVerb):
    def match(self, evt, course_id):
        return (evt['event_type'] == 'problem_check' and
                evt['event_source'] == 'server')

    def convert(self, evt, course_id):
        verb = self.get_verb()
        obj = Activity(
            id=evt['event']['problem_id'],
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': evt['context']['module']['display_name']}),
                type="http://adlnet.gov/expapi/activities/question"
            )
        )
        return verb, obj
