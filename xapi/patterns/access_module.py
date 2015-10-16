import re

from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.verbs import AccessVerb


# learner_accesses_a_module
class AccessModuleRule(BasePattern, AccessVerb):
    def match(self, evt, course_id):
        return (re.match(r'^/courses/.*/courseware/?\w*', evt['event_type']) or
                evt['event_type'] == "seq_goto" or
                evt['event_type'] == "seq_next" or
                evt['event_type'] == "seq_prev")

    def convert(self, evt, course_id):
        verb = self.get_verb()
        seq_condition = (
            evt['event_type'] == "seq_goto" or
            evt['event_type'] == "seq_next" or
            evt['event_type'] == "seq_prev"
        )
        if seq_condition:
            module = evt['page'].split('/')[-2:][0]+"_"+evt['event']['new']
            obj = Activity(
                id=evt['page']+"/"+evt['event']['new'],
                definition=ActivityDefinition(
                    name=LanguageMap({'en-US': module}),
                    type="http://adlnet.gov/expapi/activities/module"
                )
            )
        else:
            module = evt['event_type'].split('/')[-2:][0]
            obj = Activity(
                id=self.fix_id(self.base_url, evt['context']['path']),
                definition=ActivityDefinition(
                    name=LanguageMap({'en-US': module}),
                    type="http://adlnet.gov/expapi/activities/module"
                )
            )
        return verb, obj
