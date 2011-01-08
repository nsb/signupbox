
from models import Account

def account(request):
    """
    Returns the current account
    """
    try:
        account = request.user.accounts.get() if request.user.is_authenticated() else None
    except Account.DoesNotExist:
        account = None

    return {
        'account': account
    }