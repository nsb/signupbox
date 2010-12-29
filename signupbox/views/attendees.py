import csv

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
from django.template.defaultfilters import date, floatformat, capfirst
from django.utils.translation import ugettext, ugettext_lazy as _

from ..wizard import FormWizard
from ..constants import *
from ..models import Event, Booking
from ..forms import attendeeactionsform_factory, AttendeesExportForm, AttendeesEmailForm

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

class AttendeesActionWizard(FormWizard):

    def parse_params(self, request, *args, **kwargs):

        account = request.user.accounts.get()
        self.event = get_object_or_404(Event, account=account, slug=kwargs['slug'])

    def get_template(self, step):
        if step == 0:
            return 'signupbox/attendees.html'
        else:
            if self.action == 'email':
                return 'signupbox/attendees_email.html'
            elif self.action == 'export':
                return 'signupbox/attendees_export.html'

    def render_template(self, request, form, previous_fields, step, context=None):

        context = context or {}
        context.update({'event':self.event})

        return super(AttendeesActionWizard, self).render_template(
            request, form, previous_fields, step, context
        )

    def process_step(self, request, form, step):
        if step == 0 and form.is_valid():
            self.action = form.cleaned_data['action']
            self.attendees = form.cleaned_data['attendees']

            if self.action == 'email':
                self.form_list = [self.form_list[0], AttendeesEmailForm]
            elif self.action == 'export':
                self.form_list = [self.form_list[0], AttendeesExportForm]
            else:
                self.form_list = [self.form_list[0]]

    def done(self, request, form_list):
        extra_args = {}
        if self.action == 'email' or self.action == 'export':
            extra_args.update(form_list[1].cleaned_data)

        return AttendeeActions().dispatch(request, self.attendees, self.action, self.event, **extra_args)

@login_required
def event_attendees(request, slug,):

        account=request.user.accounts.get()
        event = get_object_or_404(Event, account=account, slug=slug)

        #query = request.GET.copy()
        #if not 'show' in query:
            #query['show'] = 'confirmed'

        #self.filter_form = RegistrationListFilterForm(query)
        #if self.filter_form.is_valid():
            #show = self.filter_form.cleaned_data['show']
            #find = self.filter_form.cleaned_data['find']

            #if show:
                #qs = qs.filter(status=show)
            #if find:
                #qs = qs.filter(registrationdata__value__icontains=find).distinct()

        attendees = event.confirmed_attendees.all()

        return AttendeesActionWizard([attendeeactionsform_factory(attendees), None])(request, slug=slug)

@login_required
def event_attendees_edit(request, slug, attendee_id):
    pass
