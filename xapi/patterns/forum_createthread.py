from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.eco_verbs import LearnerPostNewForumThreadVerb


class ForumCreateThreadRule(BasePattern, LearnerPostNewForumThreadVerb):
    def match(self, evt, course_id):
        return evt['event_type'] == "edx.forum.thread.created"

    def convert(self, evt, course_id):
        obj = None
        title = None
        try:
            event_data = evt['event']
            title = event_data.get('title', None)
        except:  # pylint: disable=bare-except
            pass
        if title:
            if isinstance(title, list):
                title = title[0]
            verb = self.get_verb()
            obj = Activity(
                id=self.fix_id(self.base_url, evt['context']['path']),
                definition=ActivityDefinition(
                    name=LanguageMap({'en-US': title}),
                    type="http://www.ecolearning.eu/expapi/activitytype/discussionthread"
                )
            )
        else:
            verb = None  # Skip the not really created post

        return verb, obj
