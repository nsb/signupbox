
from django.http import Http404, HttpResponseRedirect
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

from objperms.models import ObjectPermission

from models import Account

def with_account(view):

    def wrapper(request, *args, **kwargs):

        account = Account.objects.by_request(request)

        if not account:
            try:
                obj_perm = ObjectPermission.objects.get(
                    user=request.user,
                    content_type=ContentType.objects.get_for_model(Account),
                    can_view = True
                )
                account = obj_perm.content_object

                return HttpResponseRedirect(
                      'http%(secure)s://%(account)s.%(host)s%(path)s' % {
                          'secure': 's' if request.is_secure() else '',
                          'account': account.name,
                          'host': '.'.join(request.get_host().rsplit('.', 2)[-2:]),
                          'path': request.get_full_path()
                      }
                )
            except ObjectPermission.DoesNotExist:
                raise Http404

        kwargs['account'] = account
        return view(request, *args, **kwargs)
    wrapper.__name__ = view.__name__
    return wrapper
