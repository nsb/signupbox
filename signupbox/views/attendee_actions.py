import csv

from django.template.defaultfilters import date, floatformat, capfirst
from django.utils.translation import ugettext, ungettext, ugettext_lazy as _
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from ..constants import *

from ..tasks import send_mail

class AttendeeActions(object):
    def dispatch(self, request, attendees, action, event, **kwargs):
        """
        Get the action named `action` and call it with `request` and
        `attendees` as arguments. `action` must be a callable attribute on
        the `AttendeeActions` instance.
        """
        action_func = getattr(self, action, None)
        if callable(action_func):
            return action_func(request, attendees, event, **kwargs)

    def export(self, request, attendees, event, format, data):
        """
        Export registration data
        - format is csv, xls or pdf
        - data is is bookings or attendees
        """

        if format == CSV_EXPORT:
            return self.export_csv(request, attendees, event, data)
        elif format == PDF_EXPORT:
            return self.export_pdf(request, attendees, event, data)
        elif format == XLS_EXPORT:
            return self.export_xls(request, attendees, event, data)

    def email(self, request, attendees, event, subject, message, receive_copy):

        send_mail.delay(
            [a.email for a in attendees],
            subject,
            message,
        )
        if receive_copy:
            send_mail.delay(
                [request.user.email],
                subject,
                message,
            )

        messages.success(request, ungettext('Email sent', 'Emails sent', attendees.count()))
        return redirect(reverse('event_attendees', kwargs={'slug':event.slug}))

    def export_csv(self, request, selected, event, data):
        """
        Export data as csv.

        """

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % event.title.encode('utf8')

        writer = csv.writer(response)

        if data == ATTENDEE_DATA:

            # attendee data

            writer.writerow(
                [capfirst(field.label).encode('utf8') for field in event.fields.all()]
            )

            for r in selected:
                writer.writerow(
                    [field.value.encode('utf8') for field in r.values.all()]
                )

        elif data == BOOKING_DATA:

            # booking data

            bookings = Booking.objects.filter(id__in=selected.values_list('booking__id', flat=True))

            writer.writerow(
                [ugettext('Booking').encode('utf8'),
                 event.fields.all()[0].label.encode('utf8'),
                 ugettext('Date and time').encode('utf8'),
                 ugettext('Ordernumber').encode('utf8'),
                 ugettext('Transaction').encode('utf8'),
                 ugettext('Amount').encode('utf8'),
                 ugettext('Currency').encode('utf8'),
                 ugettext('Cardtype').encode('utf8'),
                 ugettext('Description').encode('utf8'),
                 ugettext('Notes').encode('utf8'),]
            )

            for b in bookings:
                writer.writerow(
                    ['#%d' % b.id,
                     str(b.attendees.order_by('id')[0]).encode('utf8') if b.attendees.order_by('id')[0] else None,
                     date(b.timestamp, "d/m/Y H:i"),
                     b.ordernum,
                     b.transaction,
                     floatformat(b.amount,-2),
                     b.currency.encode('utf8'),
                     b.cardtype.encode('utf8'),
                     b.description.encode('utf8'),
                     b.notes.encode('utf-8'),]
                )

        return response
