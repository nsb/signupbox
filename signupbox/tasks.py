from datetime import datetime, date, time, timedelta

from django.core.mail import send_mass_mail, send_mail
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.db.models import signals, Max, Sum

from celery.decorators import task, periodic_task

from activities.models import Activity
from models import Booking, BookingAggregation, Attendee

@task
def async_send_mail(recipients, subject, message):
    sender = 'noreply@%s' % Site.objects.get_current().domain
    send_mass_mail(((subject, message, sender, [recipient]) for recipient in recipients))

@task
def process_booking(booking):
    """
    Send mails on booking confirmed
    """
    send_mass_mail(
        ((render_to_string(
            'signupbox/mails/register_email_subject.txt' if index else 'signupbox/mails/register_email_subject_registrant.txt',
            {'event': booking.event, 'booking': booking, 'attendee': attendee}
        ), render_to_string(
            'signupbox/mails/register_email.txt' if index else 'signupbox/mails/register_email_registrant.txt',
            {'event': booking.event, 'booking': booking, 'attendee': attendee},
        ), 'noreply@%s' % Site.objects.get_current().domain, 
        [attendee.email])
            for index, attendee in enumerate(booking.attendees.all()) if attendee.email
        )
    )

    Activity.objects.create(
        content_object = booking.event,
        activity = booking.activity,
    )

    ba, created = BookingAggregation.objects.get_or_create(date=date.today(), event=booking.event)
    ba.count = Attendee.objects.filter(
        booking__in=Booking.objects.today().filter(event=booking.event), status='confirmed'
    ).aggregate(Sum('attendee_count'))['attendee_count__sum'] or 0
    ba.save()

@task
def account_send_invites(invites, message):
    """
    Send out invites to new account members
    """
    send_mass_mail([
        (render_to_string(
            'signupbox/mails/account_invite_subject.txt', {'invite':invite, 'site':Site.objects.get_current()}
          ),
          render_to_string(
            'signupbox/mails/account_invite_message.txt', {'invite':invite, 'message':message, 'site':Site.objects.get_current()}
          ),
          'noreply@%s' % Site.objects.get_current().domain,
          [invite.email]) for invite in invites
    ])


@periodic_task(run_every=timedelta(hours=1))
def process_booking_aggregations():
    pass
