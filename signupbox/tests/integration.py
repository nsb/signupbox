# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django import test
from django.test.client import Client
from django.core.urlresolvers import reverse

from ..models import Event, Booking

class IntegrationTestCase(test.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testSignupbox(self):

        #Integration tests

        #Signup
        response = self.client.post(
            reverse('signup',),
            {'accountname':'myaccount', 'email':'myemail@example.com', 'password':'mypassword', 'password2':'mypassword',}
        )
        self.failUnlessEqual(response.status_code, 302)

        response = self.client.get(reverse('index'))
        self.failUnlessEqual(response.status_code, 200)

        #Create an event
        response = self.client.post(
            reverse('event_create'), 
            {
                'title':'mytitle',
                'begins_0':date.today() + timedelta(days=7),
                'begins_1_0':'9',
                'begins_1_1':'00',
                'ends_0': date.today() + timedelta(days=7),
                'ends_1_0':'16',
                'ends_1_1':'00',
            },
        )
        self.failUnlessEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(title='mytitle').exists())

        #Edit the event
        response = self.client.post(
            reverse('event_edit', kwargs={'slug':'mytitle'},), 
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
        self.assertFalse(Event.objects.filter(title='mytitle').exists())
        self.assertTrue(Event.objects.filter(title='mynewtitle').exists())

        #Get the event site
        response = self.client.get(
            reverse('event_site', kwargs={'slug':'mytitle',}),
            HTTP_HOST='myaccount.example.com'
        )
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get(
            reverse('event_register', kwargs={'slug':'mytitle',}),
            HTTP_HOST='myaccount.example.com'
        )
        self.failUnlessEqual(response.status_code, 200)

        #Register for event
        fields = list(Event.objects.get(slug='mytitle').fields.all())

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
            reverse('event_register', kwargs={'slug':'mytitle',}),
            data,
            HTTP_HOST='myaccount.example.com'
        )
        self.failUnlessEqual(response.status_code, 302)
        self.assertEquals(Event.objects.get(slug='mytitle').bookings.count(), 1) 
        self.assertEquals(Event.objects.get(slug='mytitle').bookings.get().attendees.count(), 2)

        response = self.client.post(
            reverse('event_confirm', kwargs={'slug':'mytitle', 'booking_id':Booking.objects.get().pk}),
            {},
            HTTP_HOST='myaccount.example.com'
        )

        response = self.client.get(
            reverse('event_complete', kwargs={'slug':'mytitle',}),
            HTTP_HOST='myaccount.example.com'
        )
        self.failUnlessEqual(response.status_code, 200)
