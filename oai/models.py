# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import hashlib
from django.contrib import admin
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone as DTZ
from djcelery.models import TaskMeta


from .utils import nstr, ndt
from .settings import OWN_SET_PREFIX, RESUMPTION_TOKEN_SALT, DISABLE_PRINT_OWN_SET_PREFIX


# An OAI data provider
class OaiSource(models.Model):
    url = models.URLField(max_length=255, unique=True)  # The URL of the OAI endpoint
    name = models.CharField(max_length=100, unique=True)  # The name of the repository as exposed by Identify
    prefix = models.CharField(max_length=100, unique=True)  # The prefix used for the virtual sets
    last_update = models.DateTimeField()  # Records with a modification date earlier than that are fetched
    day_granularity = models.BooleanField()  # True if the endpoint does not store datetimes but only dates

    harvester = models.CharField(max_length=128, null=True, blank=True)  # Task id of the harvester
    status = models.CharField(max_length=255, null=True, blank=True)  # Status of the harvester
    last_change = models.DateTimeField(auto_now=True)  # Last change made to this model

    class Meta(object):
        app_label = 'oai'

    def __unicode__(self):
        return self.name

    def sets(self):
        return OaiSet.objects.filter(source=self.pk)

    def records(self):
        return OaiRecord.objects.filter(source=self.pk)

    def harvesting(self):
        return self.harvester_state() not in ['SUCCESS', 'FAILURE', 'REVOKED', 'DELETED']

    def harvester_task(self):
        try:
            return TaskMeta.objects.get(task_id=self.harvester)
        except ObjectDoesNotExist:
            pass

    def harvester_state(self):
        task = self.harvester_task()
        if task:
            return task.status
        return 'DELETED'


# An error encountered while harvesting an OAI data provider
class OaiError(models.Model):
    source = models.ForeignKey(OaiSource)
    timestamp = models.DateTimeField(auto_now=True)
    text = models.CharField(max_length=512, null=True, blank=True)

    class Meta(object):
        app_label = 'oai'

    def __unicode__(self):
        return self.text


# An OAI set. If it is not associated with a source, it means that it is introduced by us
class OaiSet(models.Model):
    source = models.ForeignKey(OaiSource, null=True, blank=True)
    name = models.CharField(max_length=512)
    fullname = models.CharField(max_length=512, null=True, blank=True)

    unique_together = ('name', 'source')

    class Meta(object):
        app_label = 'oai'

    # pylint: disable=E1101
    def __unicode__(self):
        prefix = OWN_SET_PREFIX
        if self.source:
            prefix = self.source.prefix
        if prefix == OWN_SET_PREFIX and DISABLE_PRINT_OWN_SET_PREFIX:
            return self.name
        else:
            return prefix+':'+self.name

    @staticmethod
    def by_representation(name):
        """
        Returns the set s such that unicode(s) == name, or None if not found
        """
        scpos = name.find(':')
        if scpos == -1:
            return None
        prefix = name[:scpos]
        try:
            if prefix != OWN_SET_PREFIX:
                source = OaiSource.objects.get(prefix=prefix)
            else:
                source = None
            return OaiSet.objects.get(source=source, name=name[scpos+1:])
        except ObjectDoesNotExist:
            return None


class OaiFormat(models.Model):
    name = models.CharField(max_length=128)
    schema = models.CharField(max_length=512, null=True, blank=True)
    namespace = models.CharField(max_length=512, null=True, blank=True)

    class Meta(object):
        app_label = 'oai'

    def __unicode__(self):
        return self.name


# A record from an OAI source
class OaiRecord(models.Model):
    source = models.ForeignKey(OaiSource)
    # Last modified by the OAI source
    timestamp = models.DateTimeField()
    # The format of the metadata
    format = models.ForeignKey(OaiFormat)
    # The unique ID of the metadata from the source
    identifier = models.CharField(max_length=128, unique=True)
    # The sets it belongs to
    sets = models.ManyToManyField(OaiSet)
    # The metadata as an XML object
    metadata = models.TextField()
    # Last updated by us
    last_modified = models.DateTimeField(auto_now=True)

    date_removed = models.DateTimeField(null=True, blank=True)

    class Meta(object):
        app_label = 'oai'

    def deleted(self):
        return self.date_removed is not None
    deleted.boolean = False

    # pylint: disable=W0221
    def delete(self):
        savenow = DTZ.now()
        self.date_removed = savenow
        self.last_modified = savenow
        self.save()

    def __unicode__(self):
        return self.identifier


class OaiRecordAdmin(admin.ModelAdmin):
    """
    Providing access to logically deleted objects
    """

    list_display = ("id", "__unicode__", "deleted")
    # list_filter = ("deleted",)

#   Commented out as using default django manager
#    def queryset(self, request):
#        qs = self.model._default_manager.all_with_deleted()
#        ordering = self.ordering or ()
#        if ordering:
#            qs = qs.order_by(*ordering)
#        return qs

    class Meta(object):
        app_label = 'oai'


# A resumption token for the output interface
class ResumptionToken(models.Model):
    date_created = models.DateTimeField(auto_now=True)
    queryType = models.CharField(max_length=64)
    set = models.ForeignKey(OaiSet, null=True, blank=True)
    metadataPrefix = models.ForeignKey(OaiFormat, null=True, blank=True)
    fro = models.DateTimeField(null=True, blank=True)
    until = models.DateTimeField(null=True, blank=True)
    offset = models.IntegerField()
    cursor = models.IntegerField()
    total_count = models.IntegerField()
    key = models.CharField(max_length=128, null=True, blank=True)

    class Meta(object):
        app_label = 'oai'

    def __unicode__(self):
        return self.key

    # pylint: disable=E1101
    def genkey(self):
        m = hashlib.md5()
        m.update('%s_%s_%d_%s_%s_%s_%s_%d' % (RESUMPTION_TOKEN_SALT, ndt(self.date_created),
                                              self.id, nstr(self.set), self.metadataPrefix,
                                              ndt(self.fro), ndt(self.until), self.offset))
        self.key = m.hexdigest()
        self.save()


# A statement that some record belongs to some set.
# class OaiSetSpec(models.Model):
#    container = models.ForeignKey(OaiSet)
#    record = models.ForeignKey(OaiRecord)
#    unique_together
#    def __unicode__(self):
#        return record.identifier + " is " + unicode(self.container)
