def account(request):
    """
    Returns the current account
    """
    return {'account': request.user.accounts.get() if request.user.is_authenticated else None}