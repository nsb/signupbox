
from django.http import Http404

from models import Account

def with_account(f):

    def wrapper(request, *args, **kwargs):

        account = Account.objects.by_request(request)

        if not account:
            raise Http404

        kwargs['account'] = account
        return f(request, *args, **kwargs)
    return wrapper
