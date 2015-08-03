# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from oai.models import *
from djcelery.models import TaskMeta


class OaiErrorInline(admin.TabularInline):
    model = OaiError
    extra = 0


class OaiSourceAdmin(admin.ModelAdmin):
    inlines = [OaiErrorInline]


class TaskMetaAdmin(admin.ModelAdmin):
        readonly_fields = ('result',)

admin.site.register(TaskMeta, TaskMetaAdmin)

admin.site.register(OaiSource, OaiSourceAdmin)
admin.site.register(OaiRecord, OaiRecordAdmin)
admin.site.register(OaiSet)
admin.site.register(OaiFormat)
admin.site.register(ResumptionToken)
