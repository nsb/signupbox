import csv

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
from django.template.defaultfilters import capfirst

from ..constants import *
from ..models import Event
from ..forms import attendeeactionsform_factory, AttendeesExportForm

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

    def export_csv(self, request, selected, event, data):
        """
        Export data as csv.

        """

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % event.title.encode('utf8')

        writer = csv.writer(response)

        if data == REGISTRATION_DATA:

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
                 event.display_label.encode('utf8'),
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
                     b.registrations.order_by('id')[0].display_value.encode('utf8') if b.registrations.order_by('id')[0].display_value else None,
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




@login_required
def event_attendees(request, slug):

    account=request.user.accounts.get()
    event = get_object_or_404(Event, account=account, slug=slug)

    attendees = event.confirmed_attendees.all()
    form_class = attendeeactionsform_factory(attendees)

    if request.method == 'POST':
        form = form_class(request.POST)
        export_form = AttendeesExportForm(request.POST)
        if form.is_valid():

            action = form.cleaned_data['action']
            attendees = form.cleaned_data['attendees']

            if action == 'export' and export_form.is_valid():
                data = export_form.cleaned_data
                return AttendeeActions().dispatch(request, attendees, action, event, **data)
    else:
        form = form_class()
        export_form = AttendeesExportForm()

    return render_to_response(
        'signupbox/attendees.html',
        RequestContext(request, {'event':event, 'form':form, 'export_form':export_form}),
    )

@login_required
def event_attendees_edit(request, slug, attendee_id):
    pass
