from django.db import models
from oai.query import OaiRecordQuerySet


class OaiRecordManager(models.Manager):
    """
    A manager to implement the 'deleted' fields for an OAI records
    http://www.openarchives.org/OAI/openarchivesprotocol.html#DeletedRecords
    """

    def get_query_set(self):
        if self.model:
            return OaiRecordQuerySet(self.model, using=self._db).filter(
                date_removed__isnull=True
            )

    def all_with_deleted(self):
        if self.model:
            return super(OaiRecordManager, self).get_query_set()

    def only_deleted(self):
        if self.model:
            return super(OaiRecordManager, self).get_query_set().filter(
                date_removed__isnull=False
            )

    def get(self, *args, **kwargs):
        return self.all_with_deleted().get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        if "pk" in kwargs:
            return self.all_with_deleted().filter(*args, **kwargs)
        return self.get_query_set().filter(*args, **kwargs)
