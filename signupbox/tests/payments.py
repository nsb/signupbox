# -*- coding: utf-8 -*-

from django import test
from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict
from django.utils.hashcompat import md5_constructor

from paypal.standard.ipn.models import PayPalIPN

from base import BaseTestCase
from ..models import Booking

class PayPalTestCase(BaseTestCase):

    def setUp(self):
        super(PayPalTestCase, self).setUp()
        self.booking = Booking.objects.create(event = self.event)

    def tearDown(self):
        self.booking.delete()

    def testPayPalPayments(self):

        PayPalIPN.objects.create(
            item_number='%s' % self.booking.pk,
            payment_status='complete',
            ipaddress='1.2.3.4',
            txn_id='123456789'
        ).send_signals()

        self.assertTrue(Booking.objects.get(pk=self.booking.pk).confirmed)

class QuickpayTestCase(BaseTestCase):

    def setUp(self):
        super(QuickpayTestCase, self).setUp()
        self.booking = Booking.objects.create(event = self.event)

    def tearDown(self):
        self.booking.delete()
        super(QuickpayTestCase, self).tearDown()

    def testQuickpayPayments(self):

        data = SortedDict([
           ('msgtype', 'authorize'),
           ('ordernumber', self.booking.ordernumber),
           ('amount', '1000'),
           ('currency', 'DKK'),
           ('time', '120101090000'),
           ('state', '1'),
           ('qpstat', '000'),
           ('qpstatmsg', 'qpstat message'),
           ('chstat', '000'),
           ('chstatmsg', 'chstat message'),
           ('merchant', self.account.merchant_id),
           ('merchantemail', 'myemail@example.com'),
           ('transaction', '0123456789'),
           ('cardtype', 'dankort'),
           ('cardnumber', ''),
        ])

        md_input = ''.join(data.values()) + self.account.secret_key
        data['md5check'] = md5_constructor(md_input).hexdigest()

        response = self.client.post(
            reverse('quickpay_callback'), 
            data,
            HTTP_HOST=self.http_host
        )

        self.assertTrue(Booking.objects.get(pk=self.booking.pk).confirmed)
