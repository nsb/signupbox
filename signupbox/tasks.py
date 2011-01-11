from celery.decorators import task
from django.core.mail import send_mass_mail, send_mail
from django.contrib.sites.models import Site

@task
def async_send_mail(recipients, subject, message):
    sender = 'noreply@%s' % Site.objects.get_current().domain
    send_mass_mail(((subject, message, sender, [recipient]) for recipient in recipients))

@task
def process_booking(booking):
    """
    Send mails on booking confirmed
    """
    send_mail('hejsa', 'davs', 'yo@example.com', ['test@example.com',],)
