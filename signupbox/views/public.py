from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

from ..decorators import with_account
from ..models import Event, Booking
from ..forms import bookingform_factory

@with_account
def event_site(request, slug, account):

    event = get_object_or_404(Event, account=account, slug=slug)

    return render_to_response(
        'signupbox/event_site.html',
        RequestContext(request, {'event':event}),
    )

@with_account
def event_register(request, slug, account):

    event = get_object_or_404(Event, account=account, slug=slug)
    formset_class = bookingform_factory(event)

    if request.method == 'POST':
        formset = formset_class(request.POST)
        if formset.is_valid():
            booking = formset.save()
            return redirect(reverse('event_confirm', kwargs={'slug':slug, 'booking_id':booking.id}))
    else:
        formset = formset_class()

    return render_to_response(
        'signupbox/event_register.html',
        RequestContext(request, {'event':event, 'formset':formset}),
    )

@with_account
def event_confirm(request, slug, booking_id, account,):

    event = get_object_or_404(Event, account=account, slug=slug)
    booking = get_object_or_404(Booking, event=event, id=booking_id)

    if request.method == 'POST':

        booking.confirmed = True
        booking.save()
        return redirect(reverse('event_complete', kwargs={'slug':slug}))

    else:
        return render_to_response(
            'signupbox/event_confirm.html', RequestContext(request, {'event':event, 'booking': booking}),
        )

@with_account
def event_complete(request, slug, account,):
    return HttpResponse('hejsa')
