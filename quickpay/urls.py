from django.conf.urls.defaults import *

urlpatterns = patterns('quickpay.views',
    (r'^$', 'postback', {}, 'quickpay_postback',),
)
