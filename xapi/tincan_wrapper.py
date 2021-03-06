from __future__ import absolute_import

from xapi.patterns import (
    AccessCourseRule,
    AccessModuleRule,
    AccessProblemRule,
    AccessWikiRule,
    AccessWikiPageRule,
    CreateWikiRule,
    EditWikiRule,
    ForumAccessRule,
    ForumCreateThreadRule,
    ForumLikesRule,
    ForumReadsRule,
    ForumReplyRule,
    LearnerEnrollMOOCRule,
    LearnerUnEnrollMOOCRule,
    LoadVideoRule,
    PlayVideoRule,
    ProblemCheckRule,
    AccessPeerAssessmentRule,
    SubmitsPeerAssessmentRule,
    SubmitsPeerFeedbackRule,
    SubmitsSelfFeedbackRule,
)


class TinCanWrapper(object):
    """Wrap edx event and translate to tincan with a set of rules"""

    def __init__(self):
        """
        Configure wrapper used by the backend.
        """

        # super(TinCanWrapper, self).__init__()
        self.patterns = [
            AccessCourseRule(),
            AccessModuleRule(),
            LearnerEnrollMOOCRule(),
            LearnerUnEnrollMOOCRule(),
            CreateWikiRule(),
            EditWikiRule(),
            AccessWikiPageRule(),
            AccessWikiRule(),
            AccessProblemRule(),
            ProblemCheckRule(),
            LoadVideoRule(),
            PlayVideoRule(),
            ForumCreateThreadRule(),
            ForumReplyRule(),
            ForumLikesRule(),
            ForumReadsRule(),
            ForumAccessRule(),
            AccessPeerAssessmentRule(),
            SubmitsPeerAssessmentRule(),
            SubmitsPeerFeedbackRule(),
            SubmitsSelfFeedbackRule()
        ]

    def to_xapi(self, evt, course_id):
        """
        Convert edx event using a list of patterns to convert. First match win
        so the order in self.patterns does matter!
        """
        for p in self.patterns:
            if p.match(evt, course_id):
                # print "MATCHED RULE " + str(type(p))
                return p.convert(evt, course_id)
        # EVENT NOT MANAGED
        return None, None
