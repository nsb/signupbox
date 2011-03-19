from datetime import datetime, date, time, timedelta

from django.core.mail import send_mass_mail, send_mail
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.db.models import signals, Max, Sum
from django.template import Context
from django.utils import translation
from django.conf import settings

from celery.decorators import task, periodic_task

from activities.models import Activity
from models import Booking, Attendee

@task
def async_send_mail(recipients, subject, message):
    sender = 'noreply@%s' % Site.objects.get_current().domain
    send_mass_mail(((subject, message, sender, [recipient]) for recipient in recipients))

@task
def process_booking(booking):
    """
    Send mails on booking confirmed
    """
    translation.activate(settings.LANGUAGE_CODE)

    send_mass_mail(
        ((render_to_string(
            'signupbox/mails/register_email_subject.txt' if index else 'signupbox/mails/register_email_subject_registrant.txt',
            context_instance=Context({'event': booking.event, 'booking': booking, 'attendee': attendee}, autoescape=False)
        ), render_to_string(
            'signupbox/mails/register_email.txt' if index else 'signupbox/mails/register_email_registrant.txt',
            context_instance=Context({'event': booking.event, 'booking': booking, 'attendee': attendee}, autoescape=False)
        ), 'noreply@%s' % Site.objects.get_current().domain, 
        [attendee.email])
            for index, attendee in enumerate(booking.attendees.order_by('id')) if attendee.email
        )
    )

    Activity.objects.create(
        content_object = booking.event,
        activity = booking.activity,
    )

@task
def account_send_invites(invites, message):
    """
    Send out invites to new account members
    """
    translation.activate(settings.LANGUAGE_CODE)

    send_mass_mail([
        (render_to_string(
            'signupbox/mails/account_invite_subject.txt',
            context_instance=Context({'invite':invite, 'site':Site.objects.get_current()}, autoescape=False)

          ),
          render_to_string(
            'signupbox/mails/account_invite_message.txt',
            context_instance=Context({'invite':invite, 'message':message, 'site':Site.objects.get_current()}, autoescape=False)
          ),
          'noreply@%s' % Site.objects.get_current().domain,
          [invite.email]) for invite in invites
    ])
