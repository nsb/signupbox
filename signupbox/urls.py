from django.conf.urls.defaults import *

urlpatterns = patterns('signupbox.views',
    (r'^signup/$', 'signup', {}, 'signup',),
    (r'^admin/add/$', 'event_create', {}, 'event_create',),
    (r'^admin/(?P<slug>[-\w]+)/$', 'event_detail', {}, 'event_detail',),
    (r'^admin/(?P<slug>[-\w]+)/edit/$', 'event_edit', {}, 'event_edit',),
    (r'^admin/$', 'index', {}, 'index',),
    (r'^(?P<slug>[-\w]+)/$', 'event_site', {}, 'event_site',),
    (r'^(?P<slug>[-\w]+)/register/$', 'event_register', {}, 'event_register',),
)