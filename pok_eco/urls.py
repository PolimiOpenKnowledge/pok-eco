from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import oai

urlpatterns = patterns('',
     url(r'', include('oai.urls'))
)

urlpatterns += (url(r'^admin/', include(admin.site.urls)),)
