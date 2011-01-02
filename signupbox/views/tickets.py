from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from ..models import Event

@login_required
def event_tickets(request, slug):

    account=request.user.accounts.get()
    event = get_object_or_404(Event, account=account, slug=slug)

    return render_to_response(
        'signupbox/event_tickets.html',
        RequestContext(request, {'event':event}),
    )