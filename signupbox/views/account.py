from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User

from ..forms import AccountForm, ProfileForm, InviteForm, PermissionsForm

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

@login_required
def account_members(request):
    account = request.user.accounts.get()

    form = InviteForm()

    members = [
        (user, PermissionsForm(initial={'is_admin':user.has_perm("change", account)}),) for user in account.users.all()
    ]

    return render_to_response(
        'signupbox/members.html',
        RequestContext(request, {'form': form, 'members': members}),
    )

@login_required
@require_http_methods(['POST'])
def account_permissions(request, user_id):
    account = request.user.accounts.get()

    user = get_object_or_404(User, pk=user_id, pk__in=account.users.values_list('pk', flat=True))

    if request.method == 'POST':
        form = PermissionsForm(request.POST)
        if form.is_valid():
            is_admin = form.cleaned_data['is_admin']
            account.set_admin_status(user, is_admin)
            messages.success(request, _('Permissions updated.'))
            return redirect(reverse('account_members'))
