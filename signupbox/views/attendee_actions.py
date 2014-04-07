import csv

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, tables, TableStyle
from reportlab.lib import styles, colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from xlwt import Workbook

from django.template.defaultfilters import date, floatformat, capfirst
from django.utils.translation import ugettext, ungettext, ugettext_lazy as _
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.conf import settings

from ..constants import *

from ..tasks import async_send_mail

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 7)
        self.drawRightString(200*mm, 20*mm,
            _("Page %(page_num)d of %(page_count)d") % {'page_num':self._pageNumber, 'page_count': page_count}
        )

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

    def _update_status(self, request, attendees, event, status):
        attendees.update(status=status)
        messages.success(request, _('Attendee status updated.'))
        return redirect(reverse('event_attendees', kwargs={'slug':event.slug}))

    def cancel(self, request, attendees, event):
        return self._update_status(request, attendees, event, 'cancelled')

    def confirm(self, request, attendees, event):
        return self._update_status(request, attendees, event, 'confirmed')

    def email(self, request, attendees, event, subject, message, receive_copy):

        async_send_mail.delay(
            [a.email for a in attendees],
            subject,
            message,
            settings.LANGUAGE_CODE
        )
        if receive_copy:
            async_send_mail.delay(
                [request.user.email],
                subject,
                message,
                settings.LANGUAGE_CODE
            )

        messages.success(request, ungettext('Email sent', 'Emails sent', attendees.count()))
        return redirect(reverse('event_attendees', kwargs={'slug':event.slug}))

    def export_csv(self, request, selected, event, data):
        """
        Export data as csv.

        """

        response = HttpResponse(mimetype='text/csv')
        # if the event has a project id, include it in the filename
        project_id_token = "_%s" % (event.project_id) if event.project_id else ""
        filename = "%s%s.csv" % (event.title.encode('utf8'), project_id_token)
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename

        writer = csv.writer(response)

        if data == ATTENDEE_DATA:

            # attendee data

            writer.writerow(
                [capfirst(field.label).encode('utf8') for field in event.fields.all()] + [ugettext('Ticket').encode('utf8')]
            )

            for r in selected:
                writer.writerow(
                    [field.value.encode('utf8') for field in r.values.all()] + [r.ticket.name.encode('utf8')]
                )

        elif data == BOOKING_DATA:

            # booking data

            bookings = event.bookings.filter(id__in=selected.values_list('booking__id', flat=True))

            writer.writerow(
                [ugettext('Booking').encode('utf8'),
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
                     date(b.timestamp, "SHORT_DATETIME_FORMAT"),
                     b.ordernumber,
                     b.transaction,
                     floatformat(b.amount,-2),
                     b.currency.encode('utf8'),
                     b.cardtype.encode('utf8'),
                     b.description.encode('utf8'),
                     b.notes.encode('utf-8'),]
                )

        return response

    def export_pdf(self, request, selected, event, data):
        """
        Export data pdf.

        """

        response = HttpResponse(mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % event.title.encode('utf8')

        style = styles.getSampleStyleSheet()
        story = []

        # headline
        story.append(
            Paragraph(
                render_to_string('signupbox/includes/export_pdf_headline.txt', {'event':event}),
                style["Heading1"],
            )
        )

        # event details
        story.append(
            Paragraph(
                render_to_string('signupbox/includes/export_pdf_details.txt', {'event':event}),
                style["Normal"],
            )
        )

        if data == ATTENDEE_DATA:

            # attendee data

            attendee_style = TableStyle([
                ('BACKGROUND', (0,0), (3,0), "#F6F6F6"),
            ])

            t = tables.Table(
                [[None,
                  event.fields.all()[0].label,
                  ugettext('Email'), ugettext('Ticket')]] + \
                [['#%d' % r.booking.id,
                  '%s %s' % (r.display_value, '(%d)' % r.attendee_count if r.attendee_count != 1 else ''),
                  r.email, r.ticket.name] for r in selected],
                  style = attendee_style,
                  hAlign = 'LEFT',
            )

            story.append(t)

        elif data == BOOKING_DATA:

            # booking data

            bookings = event.bookings.filter(id__in=selected.values_list('booking__id', flat=True))

            for booking in bookings:
                story.append(Paragraph(
                    render_to_string('signupbox/includes/export_pdf_booking.txt',{'booking':booking}),
                    style["Normal"]),
                )

        doc = SimpleDocTemplate(response)
        doc.build(story, canvasmaker=NumberedCanvas)

        return response

    def export_xls(self, request, selected, event, data):
        """
        Export data excel

        """

        wb = Workbook()

        if data == ATTENDEE_DATA:

            ws = wb.add_sheet(_('Attendee data'))

            for column, field in enumerate(event.fields.all()):
                ws.row(0).write(column, capfirst(field.label))
            ws.row(0).write(event.fields.count(), capfirst(_('Attendee count')))
            ws.row(0).write(event.fields.count() + 1, capfirst(_('Ticket')))

            for row, r in enumerate(selected):
                for column, field in enumerate(r.values.all()):
                    ws.row(row + 1).write(column, field.value)
                ws.row(row + 1).write(event.fields.count(), '%d' % r.attendee_count)
                ws.row(row + 1).write(event.fields.count() + 1, '%s' % r.ticket.name)

        elif data == BOOKING_DATA:

            ws = wb.add_sheet(_('Booking data'))

            bookings = event.bookings.filter(id__in=selected.values_list('booking__id', flat=True))

            column_names = [
                ugettext('Booking'),
                ugettext(event.fields.all()[0].label),
                ugettext('Date and time'),
                ugettext('Ordernumber'),
                ugettext('Transaction'),
                ugettext('Amount'),
                ugettext('Currency'),
                ugettext('Cardtype'),
                ugettext('Description'),
                ugettext('Notes'),
            ]

            for column, name in enumerate(column_names):
                ws.row(0).write(column, name)

            for row, b in enumerate(bookings):

                column_data = [
                    '#%d' % b.id,
                    b.attendees.order_by('id')[0].display_value if b.attendees.order_by('id')[0].display_value else None,
                    date(b.timestamp, "d/m/Y H:i"),
                    b.ordernumber,
                    b.transaction,
                    floatformat(b.amount,-2),
                    b.currency,
                    b.cardtype,
                    b.description,
                    b.notes,
                ]

                for column, data in enumerate(column_data):
                    ws.row(row + 1).write(column, data)

        # if the event has a project id, include it in the filename
        project_id_token = "_%s" % (event.project_id) if event.project_id else ""
        filename = "%s%s.xls" % (event.title.encode('utf8'), project_id_token)
        response = HttpResponse(mimetype='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename

        wb.save(response)

        return response
