from datetime import date

from django import template
from django.utils.translation import ugettext_lazy as _
from django.db.models import Min, Max
from django.template import defaultfilters
from django.conf import settings

register = template.Library()

@register.simple_tag
def paypal_url():
    return getattr(settings, 'PAYPAL_URL', 'https://www.paypal.com/cgi-bin/webscr')

@register.simple_tag
def quickpay_url():
    return getattr(settings, 'QUICKPAY_URL', 'https://secure.quickpay.dk/form/')

@register.simple_tag
def ticket_summary_price(ticket, attendees):
    return '%d %s' % (ticket.price * len(attendees), ticket.event.get_currency_display()) if ticket.price else _('Free')

@register.simple_tag
def price_range(tickets):
    current_tickets = tickets.exclude(offered_from__gt=date.today(), offered_to__lt=date.today())
    min_ticket = current_tickets.aggregate(Min('price'))['price__min']
    max_ticket = current_tickets.aggregate(Max('price'))['price__max']

    if min_ticket == max_ticket:
        return defaultfilters.floatformat(min_ticket)
    else:
        return '%s - %s' % (defaultfilters.floatformat(min_ticket), defaultfilters.floatformat(max_ticket))
