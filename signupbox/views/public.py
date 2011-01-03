from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.views.decorators.csrf import csrf_view_exempt

from ..decorators import with_account
from ..models import Event, Booking, Ticket
from ..forms import bookingform_factory, emptybookingform_factory, ConfirmForm, QuickPayForm, PaypalForm

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
        RequestContext(request, {'event':event, 'formset':formset, 'empty_form':emptybookingform_factory(event, True)}),
    )

@with_account
@csrf_view_exempt
def event_confirm(request, slug, booking_id, account,):

    event = get_object_or_404(Event, account=account, slug=slug)
    booking = get_object_or_404(Booking, event=event, id=booking_id)

    amount = Ticket.objects.filter(
        attendees__id__in=booking.attendees.values_list('id', flat=True)
    ).aggregate(Sum('price'))['price__sum']

    form_class = PaypalForm if amount else ConfirmForm

    if request.method == 'POST':

        form = form_class()
        if form.is_valid():
            booking.confirmed = True
            booking.save()
            return redirect(reverse('event_complete', kwargs={'slug':slug}))
    else:

        form = form_class()

        return render_to_response(
            'signupbox/event_confirm.html', RequestContext(request, {'event':event, 'booking': booking, 'form':form}),
        )

@with_account
def event_complete(request, slug, account,):
    return HttpResponse('hejsa')
