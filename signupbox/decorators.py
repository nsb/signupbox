
from django.http import Http404

from models import Account

def with_account(view):

    def wrapper(request, *args, **kwargs):

        account = Account.objects.by_request(request)

        if not account:
            raise Http404

        kwargs['account'] = account
        return view(request, *args, **kwargs)
    wrapper.__name__ = view.__name__
    return wrapper
