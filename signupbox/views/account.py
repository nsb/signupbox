from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext, ungettext, ugettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User

from ..models import AccountInvite
from ..forms import AccountForm, ProfileForm, InviteForm, PermissionsForm, InviteAcceptForm
from ..tasks import account_send_invites

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

    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            new_invites = [
                AccountInvite.objects.create(
                    account = account,
                    email = email,
                    is_admin = form.cleaned_data.get('is_admin', False),
                    invited_by = request.user,
                ) for email in form.cleaned_data['email_addresses']
            ]
            account_send_invites.delay(new_invites, form.cleaned_data['message'])

            messages.success(
                request, 
                ungettext('Invitation sent.', 'Invitations sent.', len(new_invites))
            )
            return redirect(reverse('account_members'))
    else:
        form = InviteForm()

    members = [
        (user, PermissionsForm(initial={'is_admin':user.has_perm("change", account)}),) for user in account.users.all()
    ]

    return render_to_response(
        'signupbox/members.html',
        RequestContext(
            request,
            {'form': form, 'members': members, 'invites':account.invites.filter(is_accepted=False, expires__gt=datetime.now())}
        ),
    )

@login_required
@require_http_methods(['POST'])
def account_members_delete(request, user_id):
    account = request.user.accounts.get()
    user = get_object_or_404(User, pk=user_id, pk__in=account.users.values_list('pk', flat=True))
    account.users.remove(user)
    messages.success(request, _('User deleted.'))
    return redirect(reverse('account_members'))

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

def account_invitation(request, key):
    account = request.user.accounts.get()
    invitation = get_object_or_404(AccountInvite, key=key, account=account, is_accepted=False, expires__gt=datetime.now())

    if request.method == 'POST':
        form = InviteAcceptForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username = form.cleaned_data['email'],
                email = form.cleaned_data['email'],
                password = form.cleaned_data['password']
            )
            account.users.add(user)
            account.set_admin_status(user, invitation.is_admin) 
            invitation.accepted = True
            invitation.save()
            return redirect(reverse('index'))
    else:
        form = InviteAcceptForm(initial = { 'email': invitation.email })

    return render_to_response(
        'signupbox/account_invitation.html',
        RequestContext(request, {'form': form, 'invitation': invitation}),
    )

@login_required
@require_http_methods(['POST'])
def account_invitation_cancel(request, key):
    account = request.user.accounts.get()
    invitation = get_object_or_404(AccountInvite, key=key, account=account)
    invitation.delete()
    messages.success(request, _('Invitation canceled.'))
    return redirect(reverse('account_members'))
