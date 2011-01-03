from django import template
from django.utils.translation import ugettext_lazy as _
from django.db.models import Min, Max
from django.template import defaultfilters

register = template.Library()

@register.simple_tag
def ticket_summary_price(ticket, attendees):
    return '%d %s' % (ticket.price * len(attendees), ticket.get_currency_display()) or _('Free')

@register.simple_tag
def price_range(tickets):
    min = tickets.aggregate(Min('price'))['price__min']
    max = tickets.aggregate(Max('price'))['price__max']

    if min == max:
        return defaultfilters.floatformat(min)
    else:
        return '%d - %d' % (defaultfilters.floatformat(min), defaultfilters.floatformat(max))