import re
from django.conf import settings
from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.eco_verbs import LearnerAccessesForumVerb


class ForumAccessRule(BasePattern, LearnerAccessesForumVerb):
    def match(self, evt, course_id):
        return re.match('/courses/'+settings.COURSE_ID_PATTERN+'/discussion/forum/?', evt['event_type'])

    def convert(self, evt, course_id):
        verb = self.get_verb()
        obj = Activity(
            id=self.fix_id(self.base_url, evt['context']['path']),
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': evt['event_type']}),
                type="http://id.tincanapi.com/activitytype/discussion"
            )
        )
        return verb, obj
