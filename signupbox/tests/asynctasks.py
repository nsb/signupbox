from ..tasks import send_mail

from django import test
from django.core import mail

class BackgroundJobsTestCase(test.TestCase):

    def testSendMail(self):
        recipients = ['recp1@example.com', 'recp2@example.com',]
        subject = 'my subject'
        message = 'my message'

        send_mail(recipients, subject, message)

        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(mail.outbox[0].subject, 'my subject')