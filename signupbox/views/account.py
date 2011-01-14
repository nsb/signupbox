from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext, ugettext_lazy as _

from ..forms import AccountForm, ProfileForm

@login_required
def account_settings(request):
    account = request.user.accounts.get()

    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, _('Settings updated.'))
            return redirect(reverse('index'))
    else:
        form = AccountForm(instance=account)

    return render_to_response(
        'signupbox/settings.html',
        RequestContext(request, {'form':form})
    )

@login_required
def account_profile(request):
    account = request.user.accounts.get()

    if request.method == 'POST':
        pass
    else:
        form = ProfileForm(instance = request.user.get_profile())

    return render_to_response(
        'signupbox/profile.html',
        RequestContext(request, {'form': form}),
    )
