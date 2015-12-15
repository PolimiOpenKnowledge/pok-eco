import re

from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.eco_verbs import LearnerAccessesAModuleVerb
from xapi.utils import get_usage_key


# learner_accesses_a_module
class AccessModuleRule(BasePattern, LearnerAccessesAModuleVerb):
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
                # "block-v1:Polimi+FIS101+2015_M9+type@sequential+block@W2M1#1
                id=evt['event']['id']+"#"+evt['event']['new'],
                definition=ActivityDefinition(
                    name=LanguageMap({'en-US': module}),
                    type="http://adlnet.gov/expapi/activities/module"
                )
            )
        else:
            module = evt['event_type'].split('/')[-2:][0]
            obj = Activity(
                id=self.get_block_id(course_id, module),
                definition=ActivityDefinition(
                    name=LanguageMap({'en-US': module}),
                    type="http://adlnet.gov/expapi/activities/module"
                )
            )
        return verb, obj

    def get_block_id(self, course_id, module_id):
        return get_usage_key(course_id, module_id)
