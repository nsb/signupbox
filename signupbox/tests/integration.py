# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django import test
from django.test.client import Client
from django.core.urlresolvers import reverse

from ..models import Event

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
