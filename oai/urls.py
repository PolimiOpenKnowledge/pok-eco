"""
URLs for OAI Integration
"""
from django.conf.urls import patterns, url

from .views import *
from .utils import OAI_ENDPOINT_NAME

# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns(
    '',
    url(r'^'+OAI_ENDPOINT_NAME+'/?$', endpoint, name='oaiEndpoint')
  )
