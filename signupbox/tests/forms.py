# -*- coding: utf-8 -*-
from datetime import datetime, date, time, timedelta

from django import test

from ..models import Account, Event
from ..forms import RegistrationForm, EventForm

class RegistrationFormTestCase(test.TestCase):

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

class EventFormTestCase(test.TestCase):
    def setUp(self):
        self.account, created = Account.objects.get_or_create(name='myaccount')

    def tearDown(self):
        self.account.delete()

    def testEventForm(self):

        f = EventForm({
              'title':'mytitle',
              'begins_0':date.today() + timedelta(days=7),
              'begins_1_0':'9',
              'begins_1_1':'00',
              'ends_0': date.today() + timedelta(days=7),
              'ends_1_0':'16',
              'ends_1_1':'00',
            },
            instance=Event(account=self.account),
        )
        self.assertTrue(f.is_valid())

