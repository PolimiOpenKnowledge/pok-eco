from tincan import (
    Verb,
    LanguageMap
)


class AccessVerb:
    @classmethod
    def get_verb(self):
        verb = Verb(
            id="http://activitystrea.ms/schema/1.0/access",
            display=LanguageMap({'en-US': "Indicates the learner accessed something"}),
        )
        return verb


class AuthorVerb:
    @classmethod
    def get_verb(self):
        verb = Verb(
            id="http://activitystrea.ms/schema/1.0/author",
            display=LanguageMap({'en-US': "Indicates the learner authored something"})
        )
        return verb


class UpdateVerb:
    @classmethod
    def get_verb(self):
        verb = Verb(
            id="http://activitystrea.ms/schema/1.0/update",
            display=LanguageMap({'en-US': "Indicates the learner updated or edited something"})
        )
        return verb


class AnsweredVerb:
    @classmethod
    def get_verb(self):
        verb = Verb(
            id="http://adlnet.gov/expapi/verbs/answered",
            display=LanguageMap({'en-US': "Indicates the learner answered a question"})
        )
        return verb


class WatchVerb:
    @classmethod
    def get_verb(self):
        verb = Verb(
            id="http://activitystrea.ms/schema/1.0/watch",
            display=LanguageMap({'en-US': 'Indicates the learner has watched video xyz'}),
        )
        return verb


class LikeVerb:
    @classmethod
    def get_verb(self):
        verb = Verb(
            id="http://activitystrea.ms/schema/1.0/like",
            display=LanguageMap({'en-US': "Indicates the learner liked a forum message"}),
        )
        return verb


class ReadVerb:
    @classmethod
    def get_verb(self):
        verb = Verb(
            id="http://activitystrea.ms/schema/1.0/read",
            display=LanguageMap({'en-US': "Indicates the learner read a forum message"}),
        )
        return verb


class CommentedVerb:
    @classmethod
    def get_verb(self):
        verb = Verb(
            id="http://adlnet.gov/expapi/verbs/commented",
            display=LanguageMap({'en-US': "Indicates the learner commented on something"}),
        )
        return verb


class CreateVerb:
    @classmethod
    def get_verb(self):
        verb = Verb(
            id="http://activitystrea.ms/schema/1.0/create",
            display=LanguageMap({'en-US': "Indicates the learner created something"}),
        )
        return verb


class SubmitVerb:
    @classmethod
    def get_verb(self):
        verb = Verb(
            id="http://activitystrea.ms/schema/1.0/submit",
            display=LanguageMap({'en-US': "Indicates the learner submitted something"}),
        )
        return verb


class RegisteredVerb:
    @classmethod
    def get_verb(self):
        verb = Verb(
            id="http://adlnet.gov/expapi/verbs/registered",
            display=LanguageMap({'en-US': "Indicates the learner registered/enrolled for MOOC"}),
        )
        return verb


class ExitedVerb:
    @classmethod
    def get_verb(self):
        verb = Verb(
            id="http://adlnet.gov/expapi/verbs/exited",
            display=LanguageMap({'en-US': "Indicates the learner leaves the MOOC"}),
        )
        return verb
