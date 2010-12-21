from datetime import datetime, timedelta, date, time
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.generic.list_detail import object_detail

from ..models import Event
from ..forms import EventForm

@login_required
def create(request):

    event = Event(account=request.user.accounts.get())

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, _('Event added.'))
            return redirect(reverse('index'))
    else:
        form = EventForm(
            instance=event,
            initial={
                'begins':datetime.combine(date.today(), time(hour=9, minute=0)) + timedelta(days=7),
                'ends': datetime.combine(date.today(), time(hour=16, minute=0)) + timedelta(days=7),
            }
        )

    return render_to_response(
        'signupbox/event_create.html',
        RequestContext(request, {'form':form})
    )

@login_required
def read(request, slug):

    account = request.user.accounts.get()

    return object_detail(
        request,
        queryset=account.events,
        slug=slug,
        template_object_name='event',
        template_name='signupbox/event_detail.html',
    )