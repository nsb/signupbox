from django.conf.urls.defaults import *


urlpatterns = patterns('signupbox.views',
    (r'^signup/$', 'signup', {}, 'signup',),
    (r'^accounts/invitation/(?P<key>[-\w]{40})/$', 'account_invitation', {}, 'account_invitation',),
    (r'^accounts/invitation/(?P<key>[-\w]{40})/cancel/$', 'account_invitation_cancel', {}, 'account_invitation_cancel',),
    (r'^admin/settings/$', 'account_settings', {}, 'account_settings',),
    (r'^admin/members/$', 'account_members', {}, 'account_members',),
    (r'^admin/members/(?P<user_id>[\d]+)/delete/$', 'account_members_delete', {}, 'account_members_delete',),
    (r'^admin/permissions/(?P<user_id>[\d]+)/$', 'account_permissions', {}, 'account_permissions',),
    (r'^admin/profile/$', 'account_profile', {}, 'account_profile',),
    (r'^admin/add/$', 'event_create', {}, 'event_create',),
    (r'^admin/(?P<slug>[-\w]+)/$', 'event_detail', {}, 'event_detail',),
    (r'^admin/(?P<slug>[-\w]+)/edit/$', 'event_edit', {}, 'event_edit',),
    (r'^admin/(?P<slug>[-\w]+)/attendees/$', 'event_attendees', {}, 'event_attendees',),
    (r'^admin/(?P<slug>[-\w]+)/attendees/(?P<attendee_id>[\d]+)/edit/$', 'event_attendees_edit', {}, 'event_attendees_edit',),
    (r'^admin/(?P<slug>[-\w]+)/booking/(?P<booking_id>[\d]+)/$', 'event_booking_detail', {}, 'event_booking_detail',),
    (r'^admin/(?P<slug>[-\w]+)/fields/$', 'event_fields', {}, 'event_fields',),
    (r'^admin/(?P<slug>[-\w]+)/tickets/$', 'event_tickets', {}, 'event_tickets',),
    (r'^admin/(?P<slug>[-\w]+)/tickets/add/$', 'event_tickets_add', {}, 'event_tickets_add',),
    (r'^admin/(?P<slug>[-\w]+)/tickets/(?P<ticket_id>[\d]+)/edit/$', 'event_tickets_edit', {}, 'event_tickets_edit',),
    (r'^admin/$', 'index', {}, 'index',),
    (r'^(?P<slug>[-\w]+)/$', 'event_site', {}, 'event_site',),
    (r'^(?P<slug>[-\w]+)/register/$', 'event_register', {}, 'event_register',),
    (r'^(?P<slug>[-\w]+)/register/confirm/(?P<booking_id>[\d]+)/$', 'event_confirm', {}, 'event_confirm',),
    (r'^(?P<slug>[-\w]+)/register/complete/$', 'event_complete', {}, 'event_complete',),
    (r'^(?P<slug>[-\w]+)/register/incomplete/$', 'event_incomplete', {}, 'event_incomplete',),
    (r'^payments/quickpay/callback/', 'quickpay_callback', {}, 'quickpay_callback'),
)

urlpatterns += patterns('',
    (r'^payments/paypal/ipn/', include('paypal.standard.ipn.urls')),
)
