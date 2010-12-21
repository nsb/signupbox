# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django import test
from django.test.client import Client
from django.core.urlresolvers import reverse

from forms import RegistrationForm

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
