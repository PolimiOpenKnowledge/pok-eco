'''
django admin pages for xapi_tracker model
'''

from django.contrib import admin
from xapi.models import TrackingLog, XapiBackendConfig


class TrackingLogAdmin(admin.ModelAdmin):
    list_display = ['dtcreated', 'user_id', 'course_id', 'statement', 'tincan_key', 'tincan_error', 'exported']
    list_filter = ['exported']
    date_hierarchy = 'dtcreated'

admin.site.register(TrackingLog)
admin.site.register(TrackingLogAdmin)
admin.site.register(XapiBackendConfig)
