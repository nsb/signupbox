# -*- coding: utf-8 -*-

from django import test

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