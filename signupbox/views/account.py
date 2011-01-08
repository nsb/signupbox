from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext, ugettext_lazy as _

from ..forms import AccountForm

@login_required
def account_settings(request):
    a = request.user.accounts.get()

    if request.method == 'POST':
        form = AccountForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            messages.success(request, _('Settings updated.'))
            return redirect(reverse('index'))
    else:
        form = AccountForm(instance=a)

    return render_to_response(
        'signupbox/settings.html',
        RequestContext(request, {'form':form})
    )