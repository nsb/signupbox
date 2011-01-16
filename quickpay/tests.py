from datetime import datetime, date, timedelta

from django import test
from django.test.client import Client

class QuickpayTestCase(test.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testQuickpay(self):

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
        self.assertRedirects(response, reverse('event_detail', kwargs={'slug':'mynewtitle',}),)
        self.assertTrue(Event.objects.filter(title='mynewtitle').exists())
