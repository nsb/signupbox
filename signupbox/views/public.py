from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.views.decorators.csrf import csrf_view_exempt

from paypal.standard.forms import PayPalPaymentsForm

from ..decorators import with_account
from ..models import Event, Booking, Ticket
from ..forms import bookingform_factory, emptybookingform_factory, ConfirmForm, QuickPayForm

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
    booking = get_object_or_404(Booking, event=event, id=booking_id, confirmed=False)

    amount = Ticket.objects.filter(
        attendees__id__in=booking.attendees.values_list('id', flat=True)
    ).aggregate(Sum('price'))['price__sum']

    form_class = PayPalPaymentsForm if amount else ConfirmForm
    template_name = 'signupbox/event_confirm_paypal.html' if amount else 'signupbox/event_confirm.html'

    if amount:
        # paypal
        initial = {
            'business':account.paypal_business,
            'amount':amount,
            'currency_code':event.currency,
            'item_number': booking.pk,
            'item_name': event.title,
            'invoice': booking.ordernum,
            'notify_url': "http://%s%s" % (request.get_host(), reverse('paypal-ipn')),
            'return_url': "http://%s%s" % (request.get_host(), reverse('event_complete', kwargs={'slug':slug})),
            'cancel_return': "http://%s%s" % (request.get_host(), reverse('event_incomplete', kwargs={'slug':slug})),
        }

    else:
        initial = {}

    if request.method == 'POST':

        form = form_class(request.POST, instance=booking, initial=initial)
        if form.is_valid():
            form.save()
            return redirect(reverse('event_complete', kwargs={'slug':slug}))
    else:
        form = form_class(initial=initial)

        return render_to_response(
            template_name,
            RequestContext(request, {'event':event, 'booking': booking, 'form':form}),
        )

@with_account
def event_complete(request, slug, account,):

    event = get_object_or_404(Event, account=account, slug=slug)

    return render_to_response('signupbox/event_complete.html', RequestContext(request, {'event': event}))

@with_account
def event_incomplete(request, slug, account,):
    return HttpResponse('davs')
