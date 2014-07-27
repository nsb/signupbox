from smtplib import SMTPException

from datetime import datetime, date, time, timedelta

import urllib2

from django.core.mail import send_mass_mail, send_mail
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.db.models import signals, Max, Sum
from django.template import Context
from django.utils import translation
from django.conf import settings

from celery import group, task
from celery.utils.log import get_task_logger

import nexmo

from activities.models import Activity
from models import Event, Booking, Attendee

logger = get_task_logger(__name__)

@task
def async_send_mail(recipients, subject, message, language_code):
    """
    Send mails asynchronyously
    """

    translation.activate(language_code)

    sender = 'noreply@%s' % Site.objects.get_current().domain
    try:
        send_mass_mail(((subject, message, sender, [recipient]) for recipient in recipients))
    except SMTPException, exc:
        async_send_mail.retry(exc=exc)

@task
def process_booking(booking, language_code):
    """
    Send mails on booking confirmed
    """
    translation.activate(language_code)

    try:
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
    except SMTPException, exc:
        process_booking.retry(exc=exc)

    Activity.objects.create(content_object = booking.event,
        activity = booking.activity)

@task
def account_send_invites(invites, message, language_code):
    """
    Send out invites to new account members
    """
    translation.activate(language_code)

    try:
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
    except SMTPException, exc:
        account_send_invites.retry(exc=exc)

@task
def send_reminder(attendee, language_code):
    # send sms reminder using nexmo

    translation.activate(settings.LANGUAGE_CODE)

    if attendee.phone and attendee.booking.event.account.sms_gateway:

        username = attendee.booking.event.account.sms_gateway_username
        password = attendee.booking.event.account.sms_gateway_password
        client = nexmo.Client(username, password)

        from_ = attendee.booking.event.account.name
        to = attendee.phone
        message = render_to_string('signupbox/sms/reminder.txt',
            context_instance=Context({'attendee':attendee, 'site':Site.objects.get_current()}, autoescape=False))

        try:
            client.send_message(message, from_, to)
        except nexmo.NexmoError, exc:
            send_reminder.retry(args=[attendee, language_code], exc=exc)

    elif attendee.email:
        # send email reminder
        if attendee.email:
            sender = attendee.booking.event.account.email
            recipient = attendee.email
            subject = attendee.booking.event.reminder_subject or render_to_string('signupbox/mails/reminder_subject.txt', context_instance=Context({'attendee': attendee}, autoescape=False))
            message = attendee.booking.event.reminder or render_to_string('signupbox/mails/reminder_body.txt',
                context_instance=Context({'attendee':attendee, 'site':Site.objects.get_current()}, autoescape=False))
            try:
                send_mail(subject, message, sender, [recipient])
            except SMTPException, exc:
                send_reminder.retry(args=[attendee, language_code], exc=exc)


@task
def send_reminders():

    translation.activate(settings.LANGUAGE_CODE)

    for event in Event.objects.filter(begins__gt=datetime.today(), reminders_sent=None):
        if event.begins and datetime.today() > event.begins - timedelta(days=event.send_reminder):

            for attendee in event.confirmed_attendees.filter(reminder_sent=None):
                send_reminder.delay(attendee, settings.LANGUAGE_CODE)
                attendee.reminder_sent = datetime.today()
                attendee.save()

            event.reminders_sent = datetime.now()
            event.save()


@task
def send_survey(attendee_id, survye_id):
    """Send a relationwise survey to a single recipient"""

    url = 'https://www.relationwise.com/rls/restapi2/send/'
    attendees = Attendee.objects.select_related(
        'booking__event').filter(pk=attendee_id)

    for attendee in attendees:
        if not attendee.email:
            return

        event = attendee.booking.event
        relationwise_survey_url = \
            ("https://www.relationwise.com/rss/automaticsurvey/diysurvey.aspx"
             "?surveyID=%(surveyId)s"
             "&email=%(email)s"
             "&name=%(name)s"
             "&signupbox=%(signupbox)s") % {
            'surveyId': event.account.relationwise_survey_id.encode('iso-8859-1'),
            'name': attendee.name.encode('iso-8859-1'),
            'signupbox': event.slug.encode('iso-8859-1'),
            'email': attendee.email.encode('iso-8859-1'),
        }

        context = Context({'event': event,
                           'attendee': attendee,
                           'relationwise_survey_url': relationwise_survey_url},
                           autoescape=False)

        translation.activate(event.language)

        sender = event.account.email
        recipient = attendee.email
        subject = render_to_string('signupbox/mails/relationwise_subject.txt',
                                   context_instance=context)
        message = render_to_string('signupbox/mails/relationwise_body.txt',
                                   context_instance=context)
        try:
            send_mail(subject, message, sender, [recipient])
        except SMTPException, exc:
            send_survey.retry(args=[attendee, language_code], exc=exc)


@task
def send_surveys(event_id):
    """Send out relationwise surveys for event"""
    try:
        event = Event.objects.select_related('booking', 'account').get(pk=event_id)
    except Event.DoesNotExist:
        return

    if not event.surveyEnabled or event.surveySent or not event.account.relationwise_survey_id:
        logger.warning("Skipping send survey for event %s." % event.title)
        return

    logger.info("Sending survey for event %s" % event.title)
    group(send_survey.s(attendee.pk, event.account.relationwise_survey_id)
        for attendee in Attendee.objects.confirmed(event))()
    event.surveySent = True
    event.save()


@task
def run_surveys():
    logger.info("Checking for surveys to be sent...")
    begins = datetime.now() - timedelta(hours=20)
    event_ids = Event.objects.filter(begins__lt=begins,
                                     surveyEnabled=True).values_list('pk', flat=True)
    logger.info("Send survey for %d events" % len(event_ids))
    group(send_surveys.s(id) for id in event_ids)()
