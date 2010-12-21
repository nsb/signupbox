from datetime import datetime, timedelta, date, time
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext, ugettext_lazy as _

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