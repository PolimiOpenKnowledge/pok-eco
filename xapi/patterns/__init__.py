from xapi.patterns.access_course import AccessCourseRule
from xapi.patterns.access_module import AccessModuleRule
from xapi.patterns.access_problem import AccessProblemRule
from xapi.patterns.access_wiki import AccessWikiRule, AccessWikiPageRule
from xapi.patterns.base import BasePattern
from xapi.patterns.enrollment import (
    LearnerUnEnrollMOOCRule,
    LearnerEnrollMOOCRule
)
from xapi.patterns.forum_access import ForumAccessRule
from xapi.patterns.forum_createthread import ForumCreateThreadRule
from xapi.patterns.forum_likes import ForumLikesRule
from xapi.patterns.forum_reads import ForumReadsRule
from xapi.patterns.forum_reply import ForumReplyRule
from xapi.patterns.manage_wiki import CreateWikiRule, EditWikiRule
from xapi.patterns.problem_check import ProblemCheckRule
from xapi.patterns.video import LoadVideoRule, PlayVideoRule
