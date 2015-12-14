import re
from django.conf import settings
from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.eco_verbs import LearnerLikedForumMessageVerb


class ForumLikesRule(BasePattern, LearnerLikedForumMessageVerb):
    def match(self, evt, course_id):
        return re.match(
            '/courses/'+settings.COURSE_ID_PATTERN+r'/discussion/(threads|comments)/[\S]+/upvote/?',
            evt['event_type']
        )

    def convert(self, evt, course_id):
        verb = self.get_verb()
        obj = Activity(
            id=self.fix_id(self.base_url, evt['context']['path']),
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': evt['event_type'].split('upvote')[0]}),
                type="http://www.ecolearning.eu/expapi/activitytype/forummessage"
            )
        )
        return verb, obj
