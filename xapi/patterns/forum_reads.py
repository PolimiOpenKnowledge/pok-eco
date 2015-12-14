import re
from django.conf import settings
from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern

from xapi.patterns.eco_verbs import LearnerReadsForumMessageVerb


class ForumReadsRule(BasePattern, LearnerReadsForumMessageVerb):
    def match(self, evt, course_id):
        reg = '/courses/'+settings.COURSE_ID_PATTERN
        reg += r'/discussion/forum/[\S]+/threads/[\S]+/?'
        return re.match(reg, evt['event_type'])

    def convert(self, evt, course_id):
        verb = self.get_verb()
        obj = Activity(
            id=self.fix_id(self.base_url, evt['context']['path']),
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': evt['event_type']}),
                type="http://www.ecolearning.eu/expapi/activitytype/forummessage"
            )
        )
        return verb, obj
