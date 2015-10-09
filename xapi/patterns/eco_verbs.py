# pylint: disable=no-init

from tincan import (
    Verb
)

from xapi.patterns.verbs import *


class LearnerAccessesMoocVerb(AccessVerb):
    pass


class LearnerAccessesAModuleVerb(AccessVerb):
    pass


class LearnerEnrollMoocVerb(RegisteredVerb):
    pass


class LearnerUnenrollMoocVerb(ExitedVerb):
    pass


# ################ ASSESSMENT ################################
class LearnerAccessesAssessmentVerb(AccessVerb):
    pass


class LearnerAnswersQuestionVerb(AnsweredVerb):
    pass


# ################ PEER ASSESSMENT ###########################
class LearnerAccessesPeerAssessmentVerb(AccessVerb):
    pass


class LearnerSubmitsAssessmentVerb(SubmitVerb):
    pass


class LearnerSubmitsPeerFeedbackVerb(SubmitVerb):
    pass


class LearnerSubmitsPeerProductVerb(SubmitVerb):
    pass


# ################ FORUM #####################################

class LearnerAccessesForumVerb(AccessVerb):
    pass


class LearnerPostNewForumThreadVerb(AuthorVerb):
    pass


class LearnerRepliesToForumMessageVerb(CommentedVerb):
    pass


class LearnerLikedForumMessageVerb(LikeVerb):
    pass


class LearnerReadsForumMessageVerb(ReadVerb):
    pass


# ################ WIKI #######################################
class LearnerAccessesWikiVerb(AccessVerb):
    pass


class LearnerAccessesWikiPageVerb(AccessVerb):
    pass


class LearnerCreatesWikiPageVerb(CreateVerb):
    pass


class LearnerEditsWikiPageVerb(UpdateVerb):
    pass


# ################ VIDEO ######################################
class LoadVideoVerb(AccessVerb):
    pass


class PlayVideoVerb(WatchVerb):
    pass
