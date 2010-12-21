from django.conf.urls.defaults import *

urlpatterns = patterns('signupbox.views',
    (r'^signup/$', 'signup', {}, 'signup',),
    (r'^add/$', 'event_create', {}, 'event_create',),
    (r'^(?P<slug>[-\w]+)/$', 'event_detail', {}, 'event_detail',),
    (r'^(?P<slug>[-\w]+)/edit/$', 'event_edit', {}, 'event_edit',),
    (r'^$', 'index', {}, 'index',),
)