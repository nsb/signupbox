from django import template
from django.template import defaultfilters
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.simple_tag
def date_span(begins, ends):
    """
    format begin and end date
    """
    default = "j. F, Y"
    if begins and not ends:
        return defaultfilters.date(begins, default)
    elif ends and not begins:
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

@register.simple_tag
def datetime_span(begins, ends):
    """
    format begin and end date
    """
    default = "j. F, Y"
    time_fmt = "H:i"
    fn = lambda dt: _('%(date)s at %(time)s') % {'date':defaultfilters.date(dt, default),'time':defaultfilters.time(dt, time_fmt),}

    same_date = begins.date() == ends.date()
    return ' - '.join((fn(begins), defaultfilters.time(ends, time_fmt) if same_date else fn(ends)))
