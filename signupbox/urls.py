from django.conf.urls.defaults import *

urlpatterns = patterns('signupbox.views',
    (r'^signup/$', 'signup', {}, 'signup',),
    (r'^$', 'index', {}, 'index',),
)