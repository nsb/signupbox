from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext, ungettext, ugettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth import authenticate, login
from django.http import HttpResponseForbidden
from django.conf import settings

from ..models import AccountInvite, RelationWiseSurvey
from ..forms import AccountForm, AccountSurveyFormSet, UserForm, ProfileForm, InviteForm, PermissionsForm, InviteAcceptForm
from ..decorators import with_account
from ..tasks import account_send_invites, export_attendee_data

@login_required
@with_account
def account_settings(request, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        survey_formset = AccountSurveyFormSet(
            request.POST, instance=account,
            queryset=RelationWiseSurvey.objects.filter(account=account))
        if form.is_valid() and survey_formset.is_valid():
            form.save()
            survey_formset.save()
            messages.success(request, _('Settings updated.'))
            return redirect(reverse('index'))
    else:
        form = AccountForm(instance=account)
        survey_formset = AccountSurveyFormSet(
            instance=account,
            queryset=RelationWiseSurvey.objects.filter(account=account))

    return render_to_response(
        'signupbox/settings.html',
        RequestContext(request, {'form':form, 'survey_formset':survey_formset})
    )

@login_required
@with_account
def account_exports(request, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    if request.method == 'POST':
        export_attendee_data.delay(account.pk, request.user.email)
        messages.success(request, _('We have sent you an email with the requested data.'))
        return redirect(reverse('account_exports'))
    else:
        pass

    return render_to_response('signupbox/exports.html',
                              RequestContext(request, {}))

@login_required
@with_account
def account_profile(request, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance = request.user)
        profile_form = ProfileForm(request.POST, instance = request.user.get_profile())
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Profile updated.'))
            return redirect(reverse('index'))
    else:
        user_form = UserForm(instance = request.user)
        profile_form = ProfileForm(instance = request.user.get_profile())

    return render_to_response(
        'signupbox/profile.html',
        RequestContext(request, {'forms': [user_form, profile_form]}),
    )

@login_required
@with_account
def account_members(request, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

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
@with_account
def account_members_add(request, account):

    if not request.user.has_perm('change', account):
        return HttpResponseForbidden()

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
            account_send_invites.delay(new_invites, form.cleaned_data['message'], settings.LANGUAGE_CODE)
            messages.success(request, ungettext('Invitation sent.', 'Invitations sent.', len(new_invites)))
            return redirect(reverse('account_members'))
    else:
        form = InviteForm()

    return render_to_response(
        'signupbox/members_add.html',
        RequestContext(request, {'form': form}),
    )

@login_required
@with_account
@require_http_methods(['POST'])
def account_members_delete(request, user_id, account):

    if not request.user.has_perm('change', account):
        return HttpResponseForbidden()

    user = get_object_or_404(User, pk=user_id, pk__in=account.users.values_list('pk', flat=True))
    account.users.remove(user)
    messages.success(request, _('User removed.'))
    return redirect(reverse('account_members'))

@login_required
@with_account
@require_http_methods(['POST'])
def account_permissions(request, user_id, account):

    if not request.user.has_perm('change', account):
        return HttpResponseForbidden()

    user = get_object_or_404(User, pk=user_id, pk__in=account.users.values_list('pk', flat=True))

    if request.method == 'POST':
        form = PermissionsForm(request.POST)
        if form.is_valid():
            is_admin = form.cleaned_data['is_admin']
            account.set_perms(user, change=is_admin)
            messages.success(request, _('Permissions updated.'))
            return redirect(reverse('account_members'))

def account_invitation(request, key):
    invitation = get_object_or_404(AccountInvite, key=key, is_accepted=False, expires__gt=datetime.now())

    if request.method == 'POST':
        form = InviteAcceptForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(username=form.cleaned_data['email'])
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username = form.cleaned_data['email'],
                    email = form.cleaned_data['email'],
                    password = form.cleaned_data['password']
                )
            invitation.account.users.add(user)
            invitation.account.set_perms(user, view=True, change=invitation.is_admin)
            invitation.is_accepted = True
            invitation.save()

            # log the user in
            user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Redirect to a success page.
                    messages.success(request, _('Welcome to your %s account.') % Site.objects.get_current().domain)
                    return redirect(reverse('index'))
                else:
                    # Return a 'disabled account' error message
                    pass
    else:
        form = InviteAcceptForm(initial = { 'email': invitation.email })

    return render_to_response(
        'signupbox/account_invitation.html',
        RequestContext(request, {'form': form, 'invitation': invitation}),
    )

@login_required
@with_account
@require_http_methods(['POST'])
def account_invitation_cancel(request, key, account):

    if not request.user.has_perm('change', account):
        return HttpResponseForbidden()

    invitation = get_object_or_404(AccountInvite, key=key, account=account)
    invitation.delete()
    messages.success(request, _('Invitation canceled.'))
    return redirect(reverse('account_members'))
