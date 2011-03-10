
from models import Account

def account(request):
    """
    Returns the current account
    """

    return {
        'account': Account.objects.by_request(request)
    }