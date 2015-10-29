import re

from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.verbs import AccessVerb
from django.conf import settings


class AccessProblemRule(BasePattern, AccessVerb):
    def match(self, evt, course_id):
        return (evt['event_type'].endswith("problem_get") and
                evt['event_source'] == 'server')

    def convert(self, evt, course_id):
        verb = self.get_verb()
        module = evt['event_type'].split('/')[-2:][0]
        obj = Activity(
            id=self.fix_id(self.base_url, evt['context']['path']),
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': evt['context']['path']}),
                type="http://adlnet.gov/expapi/activities/question"
            )
        )
        return verb, obj
