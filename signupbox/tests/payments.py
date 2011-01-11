# -*- coding: utf-8 -*-

from django import test

from paypal.standard.ipn.models import PayPalIPN

class PayPalTestCase(test.TestCase):

    pass
    #def testPayPalPayments(self):

        #PayPalIPN.objects.create(
            #item_number='1',
            #payment_status='complete',
            #ipaddress='1.2.3.4',
            #txn_id='123456789'
        #).send_signals()