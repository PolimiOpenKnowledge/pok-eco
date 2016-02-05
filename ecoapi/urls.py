"""
URLs for mobile WEBAPI
"""
from django.conf.urls import patterns, url


# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns(
    '',
    url(r'^users/(?P<eco_user_id>[^/]+)/courses', 'ecoapi.views.user_courses', name='ecoapi_user_courses'),
    url(r'^teachers/(?P<id_teacher>[^/]+)', 'ecoapi.views.teacher_view', name='ecoapi_teacher'),
    url(r'^heartbeat', 'ecoapi.views.heartbeat', name='ecoapi_heartbeat'),
    url(r'^tasks/{course_key}$'.format(settings.COURSE_ID_PATTERN), 'ecoapi.views.tasks', name='ecoapi_tasks'),
)
