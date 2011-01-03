from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext, ugettext_lazy as _

from ..models import Event, Ticket
from ..forms import TicketForm

@login_required
def event_tickets(request, slug):

    account=request.user.accounts.get()
    event = get_object_or_404(Event, account=account, slug=slug)

    return render_to_response(
        'signupbox/event_tickets.html',
        RequestContext(request, {'event':event}),
    )

@login_required
def event_tickets_edit(request, slug, ticket_id):

    account=request.user.accounts.get()
    event = get_object_or_404(Event, account=account, slug=slug)
    ticket = get_object_or_404(Ticket, event__slug=slug, id=ticket_id)

    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            messages.success(request, _('Ticket updated.'))
            return redirect(reverse('event_tickets', kwargs={'slug':slug}))
    else:
        form = TicketForm(instance=ticket)

    return render_to_response(
        'signupbox/event_tickets_edit.html',
        RequestContext(request, {'event':event, 'ticket':ticket, 'form':form})
    )