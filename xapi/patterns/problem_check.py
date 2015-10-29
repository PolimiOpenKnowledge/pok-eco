import re

from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.verbs import AnsweredVerb
from django.conf import settings


class ProblemCheckRule(BasePattern, AnsweredVerb):
    def match(self, evt, course_id):
        return (evt['event_type'] == 'problem_check' and
                evt['event_source'] == 'server'
                )

    def convert(self, evt, course_id):
        verb = self.get_verb()
        obj = Activity(
            id=self.fix_id(self.base_url, evt['event']['problem_id']),
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': evt['context']['module']['display_name']}),
                type="http://adlnet.gov/expapi/activities/question"
            )
        )
        return verb, obj
