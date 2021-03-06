
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.formtools.wizard import FormWizard
from django.http import HttpResponseForbidden

from ..constants import *
from ..models import Account, Event, Booking, Attendee, Field, Ticket
from ..forms import attendeeactionsform_factory, AttendeesExportForm, AttendeesEmailForm, attendeeform_factory, BookingForm, FilterForm
from ..decorators import with_account
from attendee_actions import AttendeeActions

class AttendeesActionWizard(FormWizard):

    def parse_params(self, request, slug, *args, **kwargs):

        account = Account.objects.by_request(request)
        self.event = get_object_or_404(Event, account=account, slug=slug)
        self.qs = Attendee.objects.filter(
            booking__event=self.event, booking__confirmed=True).order_by('display_value')

        query = request.GET.copy()
        if not 'show' in query:
            query['show'] = ATTENDEE_CONFIRMED

        self.filter_form = FilterForm(query)
        if self.filter_form.is_valid():
            show = self.filter_form.cleaned_data['show']
            find = self.filter_form.cleaned_data['find']

            if show:
                self.qs = self.qs.filter(status=show)
            if find:
                self.qs = self.qs.filter(values__value__icontains=find).distinct()

        self.form_list = [attendeeactionsform_factory(self.qs), None]

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
        context.update({'event':self.event, 'attendees': self.qs, 'filter_form':self.filter_form})

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

    def security_hash(self, request, form):
        return 'test'

    def done(self, request, form_list):
        extra_args = {}
        if self.action == 'email' or self.action == 'export':
            extra_args.update(form_list[1].cleaned_data)

        return AttendeeActions().dispatch(
            request, self.attendees, self.action, self.event, **extra_args)

@login_required
@with_account
def event_attendees(request, slug, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    return AttendeesActionWizard([None, None])(request, slug=slug)

@login_required
@with_account
def event_attendees_edit(request, slug, attendee_id, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    event = get_object_or_404(Event, account=account, slug=slug)
    attendee = get_object_or_404(Attendee, booking__event=event, id=attendee_id)

    form_class = attendeeform_factory(event, False, instance=attendee)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Attendee updated.'))
            return redirect(reverse('event_attendees', kwargs={'slug':slug}))
    else:
        initial = {'ticket':attendee.ticket}
        for data in attendee.values.all():
            # fix boolean field
            value = False if data.value.lower() == "false" else True if data.field.type == CHECKBOX_FIELD else data.value
            initial[data.field.name] = value

        form = form_class(initial=initial)

    return render_to_response(
        'signupbox/attendee_edit.html',
        RequestContext(request, {'event':event, 'attendee': attendee, 'form':form}),
    )

@login_required
@with_account
def event_attendees_add(request, slug, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    event = get_object_or_404(Event, account=account, slug=slug)
    form_class = attendeeform_factory(event, False)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save(booking=Booking.objects.create(event=event, confirmed=True))
            messages.success(request, _('Attendee added.'))
            return redirect(reverse('event_attendees', kwargs={'slug':slug}))
    else:
        form = form_class()

    return render_to_response(
        'signupbox/attendee_add.html',
        RequestContext(request, {'event':event, 'form':form}),
    )

@login_required
@with_account
def event_booking_detail(request, slug, booking_id, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    event = get_object_or_404(Event, account=account, slug=slug)
    booking = get_object_or_404(Booking, event=event, id=booking_id)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, _('Booking updated.'))
            return redirect(reverse('event_attendees', kwargs={'slug':slug}))
    else:
        form = BookingForm(instance=booking)

    return render_to_response(
        'signupbox/booking_detail.html',
        RequestContext(request, {'event':event, 'booking':booking, 'form':form,}),
    )
