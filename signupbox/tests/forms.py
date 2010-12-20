# -*- coding: utf-8 -*-

from django import test

from ..forms import RegistrationForm

class FormTestCase(test.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRegistrationForm(self):

        #Valid form submission
        f = RegistrationForm(
            {'accountname':'myaccount', 'email':'myemail@example.com', 'password':'mypassword', 'password2':'mypassword',}
        )
        self.assertTrue(f.is_valid())

        #Do not allow different passwords
        f = RegistrationForm(
            {'accountname':'myaccount', 'email':'myemail@example.com', 'password':'mypassword', 'password2':'myotherpassword',}
        )
        self.assertFalse(f.is_valid())
