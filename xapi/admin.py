'''
django admin pages for xapi_tracker model
'''

from xapi.models import TrackingLog
from django.contrib import admin


class TrackingLogAdmin(admin.ModelAdmin):
    list_display = ['dtcreated', 'user_id', 'course_id', 'statement', 'tincan_key', 'tincan_error', 'exported']
    list_filter = ['exported']
    date_hierarchy = 'dtcreated'
admin.site.register(TrackingLog, TrackingLogAdmin)
