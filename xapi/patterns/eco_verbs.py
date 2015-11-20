# pylint: disable=no-init
"""Eco Verbs definitions.
All those verbs are used to implement the xapi translation
of edx events according to what ECO define as interesting verbs
for ECO platform as stated in
https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM

Please note that only edx events already tracked will be translated in xapi
"""
from xapi.patterns.verbs import (
    AccessVerb,
    RegisteredVerb,
    ExitedVerb,
    AnsweredVerb,
    SubmitVerb,
    AuthorVerb,
    CommentedVerb,
    LikeVerb,
    ReadVerb,
    CreateVerb,
    UpdateVerb,
    WatchVerb
)


class LearnerAccessesMoocVerb(AccessVerb):
    """
    This implement Learner accesses Mooc as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.i2bnof6of0kg
    """
    pass


class LearnerAccessesAModuleVerb(AccessVerb):
    """
    This implement Learner accesses a module as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.pel162knvru1
    """
    pass


class LearnerEnrollMoocVerb(RegisteredVerb):
    """
    This implement Learner enrolls in Mooc as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.r955zky4xzo
    """
    pass


class LearnerUnenrollMoocVerb(ExitedVerb):
    """
    This implement Learner unenrolls in Mooc as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.auvfsip7khry
    """
    pass


# ################ ASSESSMENT ################################
class LearnerAccessesAssessmentVerb(AccessVerb):
    """
    This implement Learner accesses assessment as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.f1yw9sp3hgb8
    """
    pass


class LearnerAnswersQuestionVerb(AnsweredVerb):
    """
    This implement Learner answers question as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.uqmvuq8mao0q
    """
    pass


# ################ PEER ASSESSMENT ###########################
class LearnerAccessesPeerAssessmentVerb(AccessVerb):
    """
    This implement Learner accesses peer assessment as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.5902ijcwi7n
    """
    pass


class LearnerSubmitsAssessmentVerb(SubmitVerb):
    """
    This implement Learner submits assessment as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.gt4c5b7w0suh
    """
    pass


class LearnerSubmitsPeerFeedbackVerb(SubmitVerb):
    """
    This implement Learner submits peer feedback as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.gz6a9a26zatz
    """
    pass


class LearnerSubmitsPeerProductVerb(SubmitVerb):
    """
    This implement Learner self assessment as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM
    """
    pass


# ################ FORUM #####################################

class LearnerAccessesForumVerb(AccessVerb):
    """
    This implement Learner accesses forum as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.k4rz2npswj0s
    """
    pass


class LearnerPostNewForumThreadVerb(AuthorVerb):
    """
    This implement Learner post new forum thread as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.cdipx3rm13v5
    """
    pass


class LearnerRepliesToForumMessageVerb(CommentedVerb):
    """
    This implement Learner replies to forum message
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.1nrok0d07qhl
    """
    pass


class LearnerLikedForumMessageVerb(LikeVerb):
    """
    This implement Learner liked forum message as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.enq85fneg7ar
    """
    pass


class LearnerReadsForumMessageVerb(ReadVerb):
    """
    This implement Learner reads forum message as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.caobact5adi5
    """
    pass


# ################ WIKI #######################################
class LearnerAccessesWikiVerb(AccessVerb):
    """
    This implement Learner accesses Wiki as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.9oheee1t495q
    """
    pass


class LearnerAccessesWikiPageVerb(AccessVerb):
    """
    This implement Learner accesses Wiki page as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.v3xklzd0n1jv
    """
    pass


class LearnerCreatesWikiPageVerb(CreateVerb):
    """
    This implement Learner creates wiki page as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.d281w8e67t0x
    """
    pass


class LearnerEditsWikiPageVerb(UpdateVerb):
    """
    This implement Learner edits wiki page as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.cqejx9u7uqjc
    """
    pass


# ################ VIDEO ######################################
class LoadVideoVerb(AccessVerb):
    """
    This implement Learner access a video resource at the moment not in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM
    """
    pass


class PlayVideoVerb(WatchVerb):
    """
    This implement Learner watches video as in
    https://docs.google.com/document/d/16d5Tw7f155RCnZrE8oDU-UGuzAatw20tOxh3-lVcUFM/edit#heading=h.4ev0znnqa20l
    """
    pass
