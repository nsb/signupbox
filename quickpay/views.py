from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def postback(request):
    pass