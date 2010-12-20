from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

@login_required
def create(request):
    return render_to_response('signupbox/event_create.html', RequestContext(request))