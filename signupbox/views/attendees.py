
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from ..wizard import FormWizard
from ..models import Event, Booking
from ..forms import attendeeactionsform_factory, AttendeesExportForm, AttendeesEmailForm
from attendee_actions import AttendeeActions

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
