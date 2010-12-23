from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from ..models import Event

@login_required
def event_attendees(request, slug):

    account=request.user.accounts.get()
    event = get_object_or_404(Event, account=account, slug=slug)

    return render_to_response(
        'signupbox/attendees.html',
        RequestContext(request, {'event':event,}),
    )
