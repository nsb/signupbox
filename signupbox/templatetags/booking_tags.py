from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.simple_tag
def ticket_summary_price(ticket, attendees):
    return ticket.price * len(attendees) or _('Free')
