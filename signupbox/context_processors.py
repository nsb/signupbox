from django.contrib.sites.models import Site

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