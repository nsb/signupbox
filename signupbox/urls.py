from django.conf.urls.defaults import *

urlpatterns = patterns('signupbox.views',
    (r'^signup/$', 'signup', {}, 'signup',),
    (r'^add/$', 'event_create', {}, 'event_create',),
    (r'^$', 'index', {}, 'index',),
)