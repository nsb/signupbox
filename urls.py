# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    (r'^myadmin/', include(admin.site.urls)),
    # (r'^sentry/', include('sentry.urls')),
    (r'^accounts/', include('auth_urls')),
    (r'^', include('signupbox.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )