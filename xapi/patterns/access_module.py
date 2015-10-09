import re

from tincan import (
    Agent,
    AgentAccount,
    Activity,
    ActivityDefinition,
    LanguageMap,
    Verb
)
from xapi.patterns.base import BasePattern
from xapi.patterns.verbs import AccessVerb


# learner_accesses_a_module
class AccessModuleRule(BasePattern, AccessVerb):
    def match(self, evt, course_id):
        return re.match('^/courses/.*/courseware/?\w*', evt['event_type'])

    def convert(self, evt, course_id):
        verb = self.get_verb()
        module = evt['event_type'].split('/')[-2:][0]
        obj = Activity(
            id=self.fix_id(self.base_url, evt['context']['path']),
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': module}),
                type="http://adlnet.gov/expapi/activities/module"
            )
        )
        return verb, obj
