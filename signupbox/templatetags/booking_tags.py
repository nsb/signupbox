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
def ticket_summary_price(ticket, attendees):
    return '%d %s' % (ticket.price * len(attendees), ticket.event.get_currency_display()) if ticket.price else _('Free')

@register.simple_tag
def price_range(tickets):
    min = tickets.aggregate(Min('price'))['price__min']
    max = tickets.aggregate(Max('price'))['price__max']

    if min == max:
        return defaultfilters.floatformat(min)
    else:
        return '%d - %d' % (defaultfilters.floatformat(min), defaultfilters.floatformat(max))