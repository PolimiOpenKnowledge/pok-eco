import json
from tincan import (
    Activity,
    ActivityDefinition,
    LanguageMap
)
from xapi.patterns.base import BasePattern
from xapi.patterns.eco_verbs import (
    LoadVideoVerb,
    PlayVideoVerb
)
from xapi.utils import get_usage_key


class BaseVideoRule(BasePattern):  # pylint: disable=abstract-method

    def convert(self, evt, course_id):
        verb = self.get_verb()  # pylint: disable=no-member
        module_id = None
        try:
            module_id = evt['event']['id']
        except TypeError:
            internal_event = json.loads(evt['event'])
            module_id = internal_event['id']
        obj = Activity(
            id=self.get_block_id(course_id, module_id),
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': module_id}),
                type="http://activitystrea.ms/schema/1.0/video"
            )
        )
        return verb, obj

    @staticmethod
    def get_block_id(course_id, module_id):
        return get_usage_key(course_id, module_id)


class PlayVideoRule(BaseVideoRule, PlayVideoVerb):
    def match(self, evt, course_id):
        return (evt['event_type'] == 'play_video' and
                evt['event_source'] == 'browser')


class LoadVideoRule(BaseVideoRule, LoadVideoVerb):
    def match(self, evt, course_id):
        return (evt['event_type'] == 'load_video' and
                evt['event_source'] == 'browser')
