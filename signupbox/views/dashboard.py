from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

from objperms.models import ObjectPermission 

from ..forms import RegistrationForm
from ..models import Account

def frontpage(request):
    return redirect(reverse('index'))

@login_required
def index(request):

    account = request.user.accounts.get()

    return render_to_response(
        'signupbox/index.html',
        RequestContext(request, {'account':account}),
    )

def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            account = Account.objects.create(name=form.cleaned_data['accountname'])
            user = User.objects.create_user(
                form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password']
            )
            account.users.add(user)

            ObjectPermission.objects.create(
                user = user,
                content_object = account,
                can_view = True,
                can_change = True,
                can_delete = True,
            )

            # log the user in
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Redirect to a success page.
                    return redirect('index')
                else:
                    # Return a 'disabled account' error message
                    pass
            else:
                # Return an 'invalid login' error message.
                pass

    else:
        form = RegistrationForm()

    return render_to_response('signupbox/signup.html', { 'form': form }, RequestContext(request))
