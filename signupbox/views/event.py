from datetime import datetime, timedelta, date, time
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.generic.list_detail import object_detail
from django.http import HttpResponseForbidden

from ..models import Event, create_default_fields, create_default_tickets, \
    RelationWiseSurvey
from ..forms import EventForm, EventCopyForm
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
            create_default_fields(event)
            create_default_tickets(event)
            event.subscribers.add(request.user)
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
        form.fields["survey"].queryset = \
            RelationWiseSurvey.objects.filter(account=account)

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
            'subscribed': event.subscribers.filter(pk=request.user.pk).exists(),
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

@login_required
@with_account
def copy(request, slug, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    event = get_object_or_404(Event, account=account, slug=slug)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=Event(account=account))
        if form.is_valid():
            new_event = form.save()

            for field in event.fields.all():
                options = field.options.all()
                field.pk = None
                field.event = new_event
                field.save()
                for option in options:
                    option.pk = None
                    option.field = field
                    option.save()

            for ticket in event.tickets.all():
                ticket.pk = None
                ticket.event = new_event
                ticket.save()

            messages.success(request, _('Event copied.'))
            return redirect(reverse('event_detail', kwargs={'slug':new_event.slug}))
    else:
        event.pk = None
        form = EventForm(instance=event)

    return render_to_response(
        'signupbox/event_copy.html',
        RequestContext(request, {'form':form, 'event':event,})
    )


@login_required
@with_account
def subscribe(request, slug, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    event = get_object_or_404(Event, account=account, slug=slug)

    if request.method == 'POST':
        event.subscribers.add(request.user)

        messages.success(request, _('Subscribed.'))
        return redirect(reverse('event_detail', kwargs={'slug':event.slug}))

@login_required
@with_account
def unsubscribe(request, slug, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    event = get_object_or_404(Event, account=account, slug=slug)

    if request.method == 'POST':
        event.subscribers.remove(request.user)

        messages.success(request, _('Unsubscribed.'))
        return redirect(reverse('event_detail', kwargs={'slug':event.slug}))

@login_required
@with_account
def archive(request, slug, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    event = get_object_or_404(Event, account=account, slug=slug)

    if request.method == 'POST':
        event.archived = True
        event.save()

        messages.success(request, _('%s was archived') % event.title)
        return redirect(reverse('index'))

@login_required
@with_account
def unarchive(request, slug, account):

    if not request.user.has_perm('view', account):
        return HttpResponseForbidden()

    event = get_object_or_404(Event, account=account, slug=slug)

    if request.method == 'POST':
        event.archived = False
        event.save()

        messages.success(request, _('%s was removed from archive') % event.title)
        return redirect(reverse('index'))
