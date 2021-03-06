from django.conf import settings
from django import test
from django.core import mail

from ..tasks import async_send_mail

class BackgroundJobsTestCase(test.TestCase):

    def testSendMail(self):
        recipients = ['recp1@example.com', 'recp2@example.com',]
        subject = 'my subject'
        message = 'my message'

        async_send_mail(recipients, subject, message, settings.LANGUAGE_CODE)

        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(mail.outbox[0].subject, 'my subject')
