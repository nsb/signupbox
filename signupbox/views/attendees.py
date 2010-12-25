from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from ..models import Event
from ..forms import attendeeactionsform_factory

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

    def export(self, request, selected, event, format, data):
        """
        Export registration data
        - format is csv or pdf
        - data is is bookings or registrations

        """

        if format == CSV_EXPORT:
            return self.export_csv(request, selected, event, data)
        elif format == PDF_EXPORT:
            return self.export_pdf(request, selected, event, data)
        elif format == XLS_EXPORT:
            return self.export_xls(request, selected, event, data)



@login_required
def event_attendees(request, slug):

    account=request.user.accounts.get()
    event = get_object_or_404(Event, account=account, slug=slug)

    attendees = event.confirmed_attendees.all()
    form_class = attendeeactionsform_factory(attendees)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            return RegistrationActions().dispatch(
                request, form.cleaned_data['attendees'], form.cleaned_data['action'], event,
            )
    else:
        form = form_class()

    return render_to_response(
        'signupbox/attendees.html',
        RequestContext(request, {'event':event, 'form':form,}),
    )

@login_required
def event_attendees_edit(request, slug, attendee_id):
    pass
