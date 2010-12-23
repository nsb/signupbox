import re

from django.http import Http404
from django.contrib.sites.models import Site

from models import Account

def with_account(f):

    def wrapper(request, *args, **kwargs):

        account = None
        #strip port number
        host = request.get_host().partition(':')[0]
        domain = Site.objects.get_current().domain

        try:
            account = Account.objects.get(domain=u'http://%s/' % host)
        except Account.DoesNotExist:
            m = re.match('(?P<account_name>[\w]+)\.%s' % domain, host, re.IGNORECASE)
            if m:
                try:
                    account = Account.objects.get(name__iexact=m.group('account_name'))
                except Account.DoesNotExist:
                    pass

        if not account:
            raise Http404

        kwargs['account'] = account
        return f(request, *args, **kwargs)
    return wrapper
