from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.eco_verbs import LearnerRepliesToForumMessageVerb


class ForumReplyRule(BasePattern, LearnerRepliesToForumMessageVerb):
    def match(self, evt, course_id):
        return evt['event_type'] == "edx.forum.response.created"

    def convert(self, evt, course_id):
        verb = self.get_verb()
        obj = Activity(
            id=self.fix_id(self.base_url, evt['context']['path']),
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': evt['referer']}),
                type="http://www.ecolearning.eu/expapi/activitytype/forummessage"
            )
        )
        return verb, obj
