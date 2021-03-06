from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.views.decorators.csrf import csrf_view_exempt
from django.utils.hashcompat import md5_constructor
from django.conf import settings
from django.utils.functional import curry
from django.utils import translation
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.models import Site

from paypal.standard.forms import PayPalPaymentsForm
from quickpay.forms import QuickpayForm
from quickpay.views import BaseQuickpayCallback

from ..models import Account, Event, Booking, Ticket, Attendee
from ..forms import registerform_factory, emptyregisterform_factory, ConfirmForm

def event_site(request, slug):

    account = Account.objects.by_request(request)
    event = get_object_or_404(Event, account=account, slug=slug)

    if event.redirect_public_page_url:
        return redirect(event.redirect_public_page_url)

    translation.activate(event.language)

    return render_to_response(
        'signupbox/event_site.html',
        RequestContext(request, {'event':event}),
    )

@csrf_view_exempt
def event_register(request, slug):

    account = Account.objects.by_request(request)
    event = get_object_or_404(Event, account=account, slug=slug)
    formset_class = registerform_factory(event)

    translation.activate(event.language)

    if request.method == 'POST':
        if not event.is_open:
            return HttpResponseBadRequest()
        formset = formset_class(request.POST)
        if formset.is_valid():
            booking = formset.save()
            return redirect(reverse('event_confirm', kwargs={'slug':slug, 'booking_id':booking.id}))
    else:
        formset = formset_class()

    return render_to_response(
        'signupbox/event_register.html' if event.is_open else 'signupbox/event_register_closed.html',
        RequestContext(request, {'event':event, 'formset':formset, 'empty_form':emptyregisterform_factory(event, True)}),
    )

@csrf_view_exempt
def event_confirm(request, slug, booking_id):

    context = {}
    account = Account.objects.by_request(request)
    event = get_object_or_404(Event, account=account, slug=slug)
    booking = get_object_or_404(Booking, event=event, id=booking_id, confirmed=False)
    amount = booking.amount

    translation.activate(event.language)

    if amount:
        if account.payment_gateway == 'quickpay':

            protocol = 3
            msgtype = 'authorize'
            language = event.language
            ordernumber = ''.join(['0' for i in range(4-len(booking.ordernumber))]) + booking.ordernumber
            autocapture = 1 if account.autocapture else 0
            cardtypelock = \
                "3d-jcb,3d-mastercard,3d-mastercard-dk,3d-visa,3d-visa-dk,american-express," \
                "american-express-dk,dankort,diners,diners-dk,jcb,mastercard,mastercard-dk,mastercard-debet-dk,visa,visa-dk,visa-electron,visa-electron-dk"
            amount = int(amount * 100)
            currency = event.currency
            merchant = account.merchant_id
            continueurl = 'http://%s%s?%s' % (
                request.get_host(),
                reverse('event_complete', kwargs={'slug': slug, 'token': booking.token}),
                request.GET.urlencode()
            )
            cancelurl = 'http://%s%s?%s' % (
                request.get_host(),
                reverse('event_incomplete', kwargs={'slug':slug}),
                request.GET.urlencode()
            )
            callbackurl = 'http://%s%s' % (
                request.get_host(),
                reverse('quickpay_callback')
            )
            md_input = ''.join(
                (str(protocol),
                  msgtype,
                  merchant,
                  language,
                  ordernumber,
                  str(amount),
                  currency,
                  continueurl,
                  cancelurl,
                  callbackurl,
                  str(autocapture),
                  cardtypelock,
                  account.secret_key.strip())
              )
            md5check = md5_constructor(md_input).hexdigest().lower()

            initial = {
                'protocol':str(protocol),
                'msgtype':msgtype,
                'merchant':merchant,
                'language':language,
                'ordernumber':ordernumber,
                'amount':str(amount),
                'currency':currency,
                'continueurl':continueurl,
                'cancelurl':cancelurl,
                'callbackurl':callbackurl,
                'autocapture':str(autocapture),
                'cardtypelock':cardtypelock,
                'md5check':md5check
            }

            template_name = 'signupbox/event_confirm_quickpay.html'
            form_class = curry(QuickpayForm, initial=initial)
        elif account.payment_gateway == 'paypal':
            initial = {
                'business':account.paypal_business,
                'amount':amount,
                'currency_code':event.currency,
                'item_number': booking.pk,
                'item_name': event.title,
                'invoice': booking.ordernumber,
                'notify_url': "http://%s%s" % (request.get_host(), reverse('paypal-ipn')),
                'return_url': "http://%s%s" % (request.get_host(), reverse('event_complete', kwargs={'slug':slug, 'token': booking.token})),
                'cancel_return': "http://%s%s" % (request.get_host(), reverse('event_incomplete', kwargs={'slug':slug})),
            }

            form_class = curry(PayPalPaymentsForm, initial=initial)
            template_name = 'signupbox/event_confirm_paypal.html'
        else:
            form_class = curry(ConfirmForm, instance=booking, initial={})
            template_name = 'signupbox/event_confirm_with_payment.html'

    else:
        form_class = curry(ConfirmForm, instance=booking, initial={})
        template_name = 'signupbox/event_confirm.html'

    if request.method == 'POST':

        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('event_complete', kwargs={'slug':slug, 'token': booking.token}))
    else:
        form = form_class()

        return render_to_response(
            template_name,
            RequestContext(request, {'event':event, 'booking': booking, 'form':form}),
        )

def event_complete(request, slug, token):

    account = Account.objects.by_request(request)
    event = get_object_or_404(Event, account=account, slug=slug)
    booking = get_object_or_404(Booking, token=token)

    translation.activate(event.language)

    return render_to_response(
        'signupbox/event_complete.html',
        RequestContext(request, {'event': event, 'booking': booking})
    )

def event_view_more(request, slug):
    event = get_object_or_404(Event, slug=slug)

    return render_to_response(
        'signupbox/event_view_more.html',
        RequestContext(request, {'event': event,})
    )


def event_incomplete(request, slug):

    account = Account.objects.by_request(request)
    event = get_object_or_404(Event, account=account, slug=slug)

    translation.activate(event.language)

    return render_to_response(
        'signupbox/event_incomplete.html',
        RequestContext(request, {'event': event})
    )

def event_terms(request, slug):

    account = Account.objects.by_request(request)
    event = get_object_or_404(Event, account=account, slug=slug)

    translation.activate(event.language)

    return render_to_response(
        'signupbox/event_terms.html',
        RequestContext(
            request,
            {'event': event, 'site': Site.objects.get_current(), 'terms': account.terms}
        )
    )

class QuickpayCallback(BaseQuickpayCallback):
    def get_secret(self, request):
        return Account.objects.by_request(request).secret_key

quickpay_callback = csrf_exempt(QuickpayCallback())
