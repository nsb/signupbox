
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse

from forms import QuickpayForm

@require_http_methods(["POST"])
def callback(request):
    form = QuickpayForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponse()