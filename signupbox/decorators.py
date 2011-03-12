
from django.http import Http404, HttpResponseRedirect
from django.contrib.sites.models import Site

from models import Account

def with_account(view):

    def wrapper(request, *args, **kwargs):

        account = Account.objects.by_request(request)

        if not account:
            try:
                return HttpResponseRedirect(
                      'http%(secure)s://%(account)s.%(host)s%(path)s' % {
                          'secure': 's' if request.is_secure() else '',
                          'account': request.user.accounts.get().name,
                          'host': request.get_host(),
                          'path': request.get_full_path()
                      }
                )
            except Account.DoesNotExist:
                raise Http404

        kwargs['account'] = account
        return view(request, *args, **kwargs)
    wrapper.__name__ = view.__name__
    return wrapper
