# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta

from django import test
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from ..models import Account, Event, Booking

class IntegrationTestCase(test.TestCase):
    def setUp(self):
        self.username, self.email, self.password = 'myusername', 'myemail@example.com', 'mypassword'
        self.account = Account.objects.create(name='myaccount')
        self.user = User.objects.create_user(self.username, self.email, self.password,)
        self.account.users.add(self.user)

        self.event = Event.objects.create(
            account=self.account,
            title='mytitle',
            begins=datetime.today() + timedelta(days=7),
            ends=datetime.today() + timedelta(days=8),
        )

        self.http_host = '.'.join((self.account.name, Site.objects.get_current().domain))

    def tearDown(self):
        self.user.delete()
        self.account.delete()

    def testSignup(self):

        #Integration tests

        #Signup
        response = self.client.post(
            reverse('signup',),
            {'accountname':'myotheraccount', 'email':'myotheremail@example.com', 'password':'mypassword', 'password2':'mypassword',}
        )
        self.failUnlessEqual(response.status_code, 302)

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
                'begins_0':date.today() + timedelta(days=7),
                'begins_1_0':'9',
                'begins_1_1':'00',
                'ends_0': date.today() + timedelta(days=7),
                'ends_1_0':'16',
                'ends_1_1':'00',
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
                'begins_0':date.today() + timedelta(days=7),
                'begins_1_0':'9',
                'begins_1_1':'00',
                'ends_0': date.today() + timedelta(days=7),
                'ends_1_0':'16',
                'ends_1_1':'00',
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
        )
        self.failUnlessEqual(response.status_code, 302)
        self.assertEquals(Event.objects.get(slug=self.event.slug).bookings.count(), 1) 
        self.assertEquals(Event.objects.get(slug=self.event.slug).bookings.get().attendees.count(), 2)

        response = self.client.post(
            reverse('event_confirm', kwargs={'slug':self.event.slug, 'booking_id':Booking.objects.get().pk}),
            {},
            HTTP_HOST=self.http_host,
        )

    def testComplete(self):
        response = self.client.get(
            reverse('event_complete', kwargs={'slug':self.event.slug,}),
            HTTP_HOST=self.http_host,
        )
        self.failUnlessEqual(response.status_code, 200)
