from datetime import datetime, date, time, timedelta

from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.humanize.templatetags.humanize import naturalday
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.sites.models import Site
from django.core.cache import cache

import gviz_api

from ..forms import RegistrationForm
from ..models import Account, Event, Booking, Attendee
from ..decorators import with_account

def dateIterator(from_date=None, to_date=None, delta=timedelta(days=1)):
    to_date = to_date or date.today()
    while from_date <= to_date:
        yield from_date
        from_date = from_date + delta
    return

def frontpage(request):
    return redirect(reverse('index'))

@login_required
@with_account
def index(request, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    return render_to_response(
        'signupbox/index.html',
        RequestContext(request, {
            'account':account, 'event_add_url': reverse('event_create')
        }),
    )

@login_required
@with_account
def event_gviz(request, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    since = date.today() - timedelta(days=6)

    events = account.events.filter(
        bookings__in=Booking.objects.filter(
            timestamp__gt=datetime.combine(since, time.min))).distinct()

    rows = []
    cache_keys = []
    cached = {}
    for d in dateIterator(from_date=since):
        for event in events:
            cache_keys.append(((d, event.pk)))
 
    cached = cache.get_many(cache_keys)
    if not cached:
        for d in dateIterator(from_date=since):
            for event in events:
                num = Attendee.objects.filter(booking__timestamp__range=(
                    datetime.combine(d, time.min), datetime.combine(d, time.max)), booking__event=event, 
                        booking__confirmed=True).aggregate(Sum('attendee_count'))['attendee_count__sum']
            cached[(d, event.pk)] = num
        cache.set_many(cached)
 
    rows = ({'date': d, 'id': id, 'attendees': cached.get((d, id))} for d, id in cached)

    description = {('date', 'date', 'Date') : [
        (str(event.id), 'number', event.title) for event in events]}

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
            account = Account.objects.create(name=form.cleaned_data['accountname'], site=Site.objects.get_current())
            user = User.objects.create_user(
                form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password']
            )
            account.users.add(user)
            account.set_perms(user, view=True, change=True)

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
