from django import forms

from ..models import Account

class AccountForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ('organization', 'street', 'payment_gateway', 'paypal_business',)
