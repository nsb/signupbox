# -*- coding: utf-8 -*-

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

        response = self.client.post(
            reverse('signup',),
            {'accountname':'myaccount', 'email':'myemail@example.com', 'password':'mypassword', 'password2':'mypassword',}
        )
        self.failUnlessEqual(response.status_code, 302)
