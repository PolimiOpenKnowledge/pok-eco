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
from xapi.patterns.eco_verbs import LearnerCreatesWikiPageVerb
from django.conf import settings


class CreateWikiRule(BasePattern, LearnerCreatesWikiPageVerb):
    def match(self, evt, course_id):
        return re.match('/courses/'+settings.COURSE_ID_PATTERN+'/wiki/\w+/_create/?', evt['event_type'])

    def convert(self, evt, course_id):
        title = None
        obj = None
        try:
            # We need to do this because we receive a string instead than a dictionary
            event_data = json.loads(evt['event'])
            title = event_data['POST'].get('title', None)
        except:
            pass
        if title:
            verb = self.get_verb()
            obj = Activity(
                id=self.fix_id(self.base_url, evt['context']['path']),
                definition=ActivityDefinition(
                    name=LanguageMap({'en-US': title}),
                    type="http://www.ecolearning.eu/expapi/activitytype/wiki"
                )
            )
        else:
            verb = None  # Skip the not really created pages
        return verb, obj
