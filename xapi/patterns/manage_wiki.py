import re
# import json
from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.eco_verbs import (
    LearnerCreatesWikiPageVerb,
    LearnerEditsWikiPageVerb
)
from django.conf import settings


class BaseWikiRule(BasePattern):  # pylint: disable=abstract-method

    def convert(self, evt, course_id):
        title = None
        obj = None
        try:
            # We need to do this because we receive a string instead than a dictionary
            # event_data = json.loads(evt['event'])
            event_data = evt['event']
            title = event_data['POST'].get('title', None)
        except:  # pylint: disable=bare-except
            pass
        if title:
            title = title[0]  # from parametervalues to single value
            verb = self.get_verb()  # pylint: disable=no-member
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


class CreateWikiRule(BaseWikiRule, LearnerCreatesWikiPageVerb):
    def match(self, evt, course_id):
        return re.match(
            '/courses/'+settings.COURSE_ID_PATTERN+'/wiki/_create/?',
            evt['event_type'])


class EditWikiRule(BaseWikiRule, LearnerEditsWikiPageVerb):
    def match(self, evt, course_id):
        return re.match(
            '/courses/'+settings.COURSE_ID_PATTERN+r'/wiki/\w+/_edit/?',
            evt['event_type'])
