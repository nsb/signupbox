from django import template
from django.template import defaultfilters

register = template.Library()

@register.simple_tag
def date_span(begins, ends):
    """
    format begin and end date
    """
    default = "j. F, Y"
    if begins and not ends:
        return defaultfilters.date(begins, default)
    elif ends and begins:
        return defaultfilters.date(ends, default)
    elif not begins and not ends:
        return '-'
    else:
        same_day = begins.day == ends.day
        same_year = begins.year == ends.year
        same_month = begins.month == ends.month
        fmt = "j." if same_month else "j. F" if same_year else default
        return ' - '.join(
            (defaultfilters.date(begins, default),) if same_day else (
                defaultfilters.date(begins, fmt), defaultfilters.date(ends, default)
            )
        )
