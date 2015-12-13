from django.contrib.sites.models import Site
from django.utils import formats

from models import Account

def account(request):
    """
    Returns the current account
    """

    return {
        'account': Account.objects.by_request(request)
    }

def site(request):
    """
    Returns the current site
    """

    return {
        'site': Site.objects.get_current()
    }

def date_format(request):
    """
    Returns the valid date format
    """

    default = formats.get_format("SHORT_DATE_FORMAT",
                                 lang=request.LANGUAGE_CODE)
    format = {'en': 'yy-mm-dd',
              'da': 'dd.mm.yy'}.get(request.LANGUAGE_CODE, default)

    return {'date_format': format}
