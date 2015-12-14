import re
from django.conf import settings
from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.eco_verbs import (
    LearnerAccessesWikiVerb,
    LearnerAccessesWikiPageVerb
)


class BaseAccessWikiRule(BasePattern):  # pylint: disable=abstract-method

    def convert(self, evt, course_id):
        verb = self.get_verb()  # pylint: disable=no-member
        obj = Activity(
            id=self.fix_id(self.base_url, evt['context']['path']),
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': evt['context']['path']}),
                type="http://www.ecolearning.eu/expapi/activitytype/wiki"
            )
        )
        return verb, obj


class AccessWikiRule(BaseAccessWikiRule, LearnerAccessesWikiVerb):
    def match(self, evt, course_id):
        return re.match(
            '/courses/'+settings.COURSE_ID_PATTERN+r'/wiki/\w+/?',
            evt['event_type'])


class AccessWikiPageRule(BaseAccessWikiRule, LearnerAccessesWikiPageVerb):
    def match(self, evt, course_id):
        return re.match(
            '/courses/'+settings.COURSE_ID_PATTERN+r'/wiki/\w+/\w+/?',
            evt['event_type'])
