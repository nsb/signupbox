from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse

from ..models import Event
from ..forms import fieldformset_factory

@login_required
def event_fields(request, slug):

    account=request.user.accounts.get()
    event = get_object_or_404(Event, account=account, slug=slug)
    formset_class = fieldformset_factory(event)

    if request.method == 'POST':
        formset = formset_class(request.POST, queryset=event.fields.all())
        if formset.is_valid():
            fields = formset.save()
            messages.success(request, _('Form fields updated.'))
            return redirect(reverse('event_detail', kwargs={'slug':slug}))
    else:
        formset = formset_class(queryset=event.fields.all())

    return render_to_response(
        'signupbox/event_fields.html',
        RequestContext(request, {'event':event, 'formset':formset,}),
    )