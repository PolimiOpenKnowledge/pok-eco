from __future__ import absolute_import

from xapi.patterns import (
    AccessCourseRule,
    AccessModuleRule,
    LearnerEnrollMOOCRule,
    LearnerUnEnrollMOOCRule
)


class TinCanWrapper(object):
    """Wrap edx event and translate to tincan with a set of rules"""

    def __init__(self, **options):
        """
        Configure wrapper used by the backend.
        """

        # super(TinCanWrapper, self).__init__(**options)
        self.patterns = [
            AccessCourseRule(**options),
            AccessModuleRule(**options),
            LearnerEnrollMOOCRule(**options),
            LearnerUnEnrollMOOCRule(**options)
        ]

    def to_xapi(self, evt, course_id):
        """
        Convert edx event using a list of patterns to convert. First match win
        """
        for p in self.patterns:
            if p.match(evt, course_id):
                return p.convert(evt, course_id)
