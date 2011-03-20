from datetime import datetime, timedelta, date, time
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.generic.list_detail import object_detail
from django.http import HttpResponseForbidden

from ..models import Event
from ..forms import EventForm
from ..decorators import with_account

@login_required
@with_account
def create(request, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    event = Event(account=account)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            messages.success(request, _('Event added.'))
            return redirect(reverse('event_detail', kwargs={'slug':event.slug}))
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
@with_account
def read(request, slug, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    event = get_object_or_404(Event, account=account, slug=slug)

    return object_detail(
        request,
        queryset=account.events,
        slug=slug,
        template_object_name='event',
        template_name='signupbox/event_detail.html',
        extra_context = {
            'attendees_url': reverse('event_attendees', kwargs={'slug': event.slug}),
            'tickets_url': reverse('event_tickets', kwargs={'slug': event.slug}),
            'fields_url': reverse('event_fields', kwargs={'slug': event.slug}),
        },
    )

@login_required
@with_account
def edit(request, slug, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    event = get_object_or_404(Event, account=account, slug=slug)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, _('Event updated.'))
            return redirect(reverse('event_detail', kwargs={'slug':slug}))
    else:
        form = EventForm(instance=event,)

    return render_to_response(
        'signupbox/event_edit.html',
        RequestContext(request, {'form':form, 'event':event,})
    )
