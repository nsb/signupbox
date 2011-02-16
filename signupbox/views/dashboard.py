from datetime import datetime, date, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.humanize.templatetags.humanize import naturalday
from django.http import HttpResponse

import gviz_api

from objperms.models import ObjectPermission 

from ..forms import RegistrationForm
from ..models import Account, Event, Booking, BookingAggregation

def dateIterator(from_date=None, to_date=None, delta=timedelta(days=1)):
    to_date = to_date or date.today()
    while from_date <= to_date:
        yield from_date
        from_date = from_date + delta
    return

def frontpage(request):
    return redirect(reverse('index'))

@login_required
def index(request):

    account = request.user.accounts.get()

    return render_to_response(
        'signupbox/index.html',
        RequestContext(request, {'account':account}),
    )

@login_required
def event_gviz(request):

    account = request.user.accounts.get()
    events = Event.objects.upcoming()

    a = {}
    for aggrs in BookingAggregation.objects.recent(days=7):
        a[aggrs.date] = a.get(aggrs.date, {})
        a[aggrs.date][aggrs.event] = a[aggrs.date].get(aggrs.event, [])
        a[aggrs.date][aggrs.event] = aggrs.count

    rows = []
    for d in dateIterator(from_date=date.today() - timedelta(days=6)):
        for event in events:
            if d in a and event in a[d]:
                count = a[d][event]
            else:
                count = 0
            rows.append({'date': d, 'id': event.id, 'attendees': count})

    description = {
        ('date', 'date', 'Date') : [(str(event.id), 'number', event.title) for event in events]
    }

    data = {}
    for index, row in enumerate(rows):
        date_tuple = (row['date'], naturalday(row['date'], "j F"))
        if date_tuple in data:
            data[date_tuple].append(row['attendees'])
        else:
            data[date_tuple] = [row['attendees']]

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    out = data_table.ToResponse()

    return HttpResponse(out, content_type='text/plain')

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
