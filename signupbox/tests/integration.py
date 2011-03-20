## -*- coding: utf-8 -*-
import re
from datetime import datetime, date, timedelta

from django import test
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.contrib.formtools.utils import security_hash
from django.utils.http import urlencode
from django.core import mail
from django.contrib.auth.models import User
from django.template import defaultfilters

from base import BaseTestCase
from ..constants import *
from ..models import Account, Event, Booking, Attendee, Ticket
from ..forms import attendeeactionsform_factory, AttendeesEmailForm

class SignupTestCase(test.TestCase):

    def testFrontpage(self):
        response = self.client.get(reverse('frontpage'))
        self.assertRedirects(response, reverse('index'), target_status_code = 302)

    def testSignup(self):

        #Integration tests

        #Signup
        response = self.client.post(
            reverse('signup',),
            {'accountname':'myotheraccount', 'email':'myotheremail@example.com', 'password':'mypassword', 'password2':'mypassword',}
        )
        self.failUnlessEqual(response.status_code, 302)

class AdminTestCase(BaseTestCase):
    def setUp(self):
        super(AdminTestCase, self).setUp()
        self.booking = Booking.objects.create(event=self.event, confirmed=True)
        self.attendee = Attendee.objects.create(
            booking=self.booking, ticket=self.event.tickets.get()
        )

    def tearDown(self):
        self.booking.delete()
        super(AdminTestCase, self).tearDown()

    def testDashboard(self):
        logged_in = self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('index'))
        self.failUnlessEqual(response.status_code, 200)

    def testCreateEvent(self):

        self.client.login(username=self.username, password=self.password)

        #Create an event
        response = self.client.post(
            reverse('event_create'), 
            {
                'title':'mynewtitle',
                'begins_0':defaultfilters.date(date.today() + timedelta(days=7), 'SHORT_DATE_FORMAT')
,
                'begins_1_0':'9',
                'begins_1_1':'00',
                'ends_0': defaultfilters.date(date.today() + timedelta(days=7), 'SHORT_DATE_FORMAT'),
                'ends_1_0':'16',
                'ends_1_1':'00',
                'status': 'open',
            },
        )
        self.failUnlessEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(title='mynewtitle').exists())

    def testEditEvent(self):

        self.client.login(username=self.username, password=self.password)

        #Edit the event
        response = self.client.post(
            reverse('event_edit', kwargs={'slug':self.event.slug},), 
            {
                'title':'mynewtitle',
                'begins_0':defaultfilters.date(date.today() + timedelta(days=7), 'SHORT_DATE_FORMAT'),
                'begins_1_0':'9',
                'begins_1_1':'00',
                'ends_0': defaultfilters.date(date.today() + timedelta(days=7), 'SHORT_DATE_FORMAT'),
                'ends_1_0':'16',
                'ends_1_1':'00',
                'status': 'open',
            },
        )
        self.failUnlessEqual(response.status_code, 302)
        self.assertFalse(Event.objects.filter(title=self.event.title).exists())
        self.assertTrue(Event.objects.filter(title='mynewtitle').exists())

    def testAttendees(self):
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(
            reverse('event_attendees', kwargs={'slug':self.event.slug,}),
        )
        self.failUnlessEqual(response.status_code, 200)

    def testAttendeeEdit(self):
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(
            reverse('event_attendees_edit', kwargs={'slug':self.event.slug, 'attendee_id':self.attendee.pk,}),
        )
        self.failUnlessEqual(response.status_code, 200)

        fields = list(self.event.fields.all())

        response = self.client.post(
            reverse('event_attendees_edit', kwargs={'slug':self.event.slug, 'attendee_id':self.attendee.pk,},), 
            {
                fields[0].name: 'Niels Sandholt Busch',
                fields[2].name: 'niels@example.com',
            },
        )
        self.failUnlessEqual(response.status_code, 302)
        self.assertTrue(self.attendee.values.filter(value='Niels Sandholt Busch').exists())

    def _testExport(self, format, data, mimetype):
        self.client.login(username=self.username, password=self.password)

        response = self.client.post(
            reverse('event_attendees', kwargs={'slug':self.event.slug,}),
            {
                'wizard_step': 0,
                '0-action':'export',
                '0-attendees': self.attendee.id,
            },
        )
        self.failUnlessEqual(response.status_code, 200)

        hash_data = {
            'action':'export',
            'attendees': self.attendee.pk,
        }

        qs = Attendee.objects.filter(booking__event=self.event).filter(status='confirmed')
        wizard_form_class = attendeeactionsform_factory(qs)

        response = self.client.post(
            reverse('event_attendees', kwargs={'slug':self.event.slug,}),
            {
                'wizard_step': 1,
                '0-action':'export',
                '0-attendees': self.attendee.pk,
                'hash_0': 'test', #security_hash(None, wizard_form_class(QueryDict(urlencode(hash_data)))),
                '1-format': format,
                '1-data': data,
            },
        )
        self.failUnlessEqual(response.status_code, 200)
        self.assertEquals(response['Content-Type'], mimetype)

    def testAttendeesExportCSV(self):
        self._testExport(CSV_EXPORT, ATTENDEE_DATA, 'text/csv')

    def testBookingExportCSV(self):
        self._testExport(CSV_EXPORT, BOOKING_DATA, 'text/csv')

    def testAttendeesExportPDF(self):
        self._testExport(PDF_EXPORT, ATTENDEE_DATA, 'application/pdf')

    def testBookingExportPDF(self):
        self._testExport(PDF_EXPORT, BOOKING_DATA, 'application/pdf')

    def testAttendeesExportXLS(self):
        self._testExport(XLS_EXPORT, ATTENDEE_DATA, 'application/vnd.ms-excel')

    def testBookingExportXLS(self):
        self._testExport(XLS_EXPORT, BOOKING_DATA, 'application/vnd.ms-excel')

    def testAttendeesMail(self):
        self.client.login(username=self.username, password=self.password)
        action = 'email'

        response = self.client.post(
            reverse('event_attendees', kwargs={'slug':self.event.slug,}),
            {
                'wizard_step': 0,
                '0-action':action,
                '0-attendees': self.attendee.pk,
            },
        )
        self.failUnlessEqual(response.status_code, 200)

        hash_data = {
            'action':action,
            'attendees': self.attendee.pk,
        }

        qs = Attendee.objects.filter(booking__event=self.event).filter(status='confirmed')
        wizard_form_class = attendeeactionsform_factory(qs)

        response = self.client.post(
            reverse('event_attendees', kwargs={'slug':self.event.slug,}),
            {
                'wizard_step': 1,
                '0-action':action,
                '0-attendees': self.attendee.pk,
                'hash_0': security_hash(None, wizard_form_class(QueryDict(urlencode(hash_data)))),
                '1-subject': 'my subject',
                '1-message': 'my message',
            },
        )
        self.failUnlessEqual(response.status_code, 302)

    def testBookingDetail(self):
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(
            reverse('event_booking_detail', kwargs={'slug':self.event.slug, 'booking_id':self.booking.pk,}),
        )
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.post(
            reverse('event_booking_detail', kwargs={'slug':self.event.slug, 'booking_id':self.booking.pk,},), 
            {'notes': 'my booking notes',},
        )
        self.failUnlessEqual(response.status_code, 302)
        self.assertEquals('my booking notes', Booking.objects.get(pk=self.booking.pk).notes)

    def testFields(self):
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(
            reverse('event_fields', kwargs={'slug':self.event.slug}),
        )
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.post(
            reverse('event_fields', kwargs={'slug':self.event.slug,},), 
            {
                'form-INITIAL_FORMS': 0,
                'form-TOTAL_FORMS': 1,
                'form-MAX_NUM_FORMS': u'',
                'form-0-label':'mylabel',
                'form-0-type':'text',
                'form-0-required':True,
                'form-0-in_extra':True,
            },
        )
        self.failUnlessEqual(response.status_code, 302)

class AccountTestCase(BaseTestCase):

    def setUp(self):
        super(AccountTestCase, self).setUp()
        self.account.set_perms(self.user, change=True)

    def tearDown(self):
        super(AccountTestCase, self).tearDown()

    def testAccountProfile(self):
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse('account_profile'))
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.post(reverse('account_profile'), {'first_name': 'myfirstname', 'last_name': 'mylastname'})
        self.failUnlessEqual(response.status_code, 302)

    def testAccountSettings(self):
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse('account_settings'))
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.post(reverse('account_settings'), {'organization': 'My organization'})
        self.failUnlessEqual(response.status_code, 302)

    def testAccountMembers(self):
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse('account_members'))
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get(reverse('account_members_add'))
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.post(
            reverse('account_members_add'), {
                'email_addresses': 'myemailaddress@example.com',
                'message': 'mymessage',
                'is_admin': '',
            },
        )
        self.failUnlessEqual(response.status_code, 302)
        self.assertEquals(len(mail.outbox), 1)

        # get the invitation key from mail
        m = re.search('accounts/invitation/(?P<key>[-\w]{40})/', mail.outbox[0].body)
        accept_key = m.group(1)

        response = self.client.get(reverse('account_invitation', kwargs={'key': accept_key}))
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.post(
            reverse('account_invitation', kwargs={'key': accept_key}), {
                'email': 'myemailaddress@example.com',
                'password': 'mypassword',
                'password2': 'mypassword',
            },
        )
        self.failUnlessEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='myemailaddress@example.com').exists())

        user = User.objects.get(username='myemailaddress@example.com')

        self.client.login(username=self.username, password=self.password)

        response = self.client.post(
            reverse('account_members_delete', kwargs={'user_id': user.pk}), {},
        )
        self.failUnlessEqual(response.status_code, 302)
        self.assertFalse(user in self.account.users.all())

class EventSiteTestCase(BaseTestCase):

    def testEventSite(self):

        #Get the event site
        response = self.client.get(
            reverse('event_site', kwargs={'slug':self.event.slug,}),
            HTTP_HOST=self.http_host
        )
        self.failUnlessEqual(response.status_code, 200)

    def testEventRegister(self):

        response = self.client.get(
            reverse('event_register', kwargs={'slug':self.event.slug,}),
            HTTP_HOST=self.http_host,
        )
        self.failUnlessEqual(response.status_code, 200)

        #Register for event
        fields = list(Event.objects.get(slug=self.event.slug).fields.all())

        data = {
            # form management data
            'form-INITIAL_FORMS': 0,
            'form-TOTAL_FORMS': 3,
            'form-MAX_NUM_FORMS': u'',
            # first attendee
            'form-0-' + fields[0].name: 'Niels Sandholt Busch',
            'form-0-' + fields[2].name: 'niels@example.com',
            #'form-0-ticket': tickets[0]['id'],
            # empty form that should be ignored
            'form-1-' + fields[0].name: '',
            'form-1-' + fields[2].name: '',
            #'form-1-ticket': '',
            # second attendee
            'form-2-' + fields[0].name: 'Ebbe Iversen',
            'form-2-' + fields[2].name: 'ebbe@example.com',
            #'form-2-ticket': tickets[0]['id'],
        }

        response = self.client.post(
            reverse('event_register', kwargs={'slug':self.event.slug,}),
            data,
            HTTP_HOST=self.http_host,
            follow=True,
        )
        next, status_code = response.redirect_chain[0]

        response = self.client.post(next, HTTP_HOST=self.http_host)

        self.failUnlessEqual(response.status_code, 302)
        self.assertEquals(self.event.bookings.count(), 1) 
        self.assertEquals(self.event.confirmed_attendees_count, 2)

    def testEventRegisterWithNoExtraForms(self):

        # remove fields from extra forms
        self.event.fields.update(in_extra=False)

        response = self.client.get(
            reverse('event_register', kwargs={'slug':self.event.slug,}),
            HTTP_HOST=self.http_host,
        )
        self.failUnlessEqual(response.status_code, 200)

        #Register for event
        fields = list(Event.objects.get(slug=self.event.slug).fields.all())

        data = {
            # form management data
            'form-INITIAL_FORMS': 0,
            'form-TOTAL_FORMS': 1,
            'form-MAX_NUM_FORMS': u'',
            # first attendee
            'form-0-' + fields[0].name: 'Niels Sandholt Busch',
            'form-0-' + fields[2].name: 'niels@example.com',
            'form-0-attendee_count': '2'
        }

        response = self.client.post(
            reverse('event_register', kwargs={'slug':self.event.slug,}),
            data,
            HTTP_HOST=self.http_host,
            follow=True,
        )
        next, status_code = response.redirect_chain[0]

        response = self.client.post(next, HTTP_HOST=self.http_host)

        self.failUnlessEqual(response.status_code, 302)
        self.assertEquals(self.event.bookings.count(), 1) 
        self.assertEquals(self.event.confirmed_attendees_count, 2)

    def testComplete(self):
        response = self.client.get(
            reverse('event_complete', kwargs={'slug':self.event.slug,}),
            HTTP_HOST=self.http_host,
        )
        self.failUnlessEqual(response.status_code, 200)

    def testIncomplete(self):
        response = self.client.get(
            reverse('event_incomplete', kwargs={'slug':self.event.slug,}),
            HTTP_HOST=self.http_host,
        )
        self.failUnlessEqual(response.status_code, 200)

    def testTerms(self):
        response = self.client.get(
            reverse('event_terms', kwargs={'slug':self.event.slug,}),
            HTTP_HOST=self.http_host,
        )
        self.failUnlessEqual(response.status_code, 200)
