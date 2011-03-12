from datetime import datetime, date, timedelta

from django import test
from django.test.client import Client
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from ..models import Account, Event, Booking, Attendee, Ticket

class BaseTestCase(test.TestCase):
    def setUp(self):
        self.username, self.email, self.password = 'myusername', 'myemail@example.com', 'mypassword'
        self.account = Account.objects.create(
            name = 'myaccount',
            merchant_id = 'merchant@example.com',
        )
        self.user = User.objects.create_user(self.username, self.email, self.password,)
        self.account.users.add(self.user)

        self.event = Event.objects.create(
            account=self.account,
            title='mytitle',
            begins=datetime.today() + timedelta(days=7),
            ends=datetime.today() + timedelta(days=8),
        )

        self.http_host = '.'.join((self.account.name, Site.objects.get_current().domain))
        self.client = Client(HTTP_HOST=self.http_host)

    def tearDown(self):
        self.user.delete()
        self.account.delete()
