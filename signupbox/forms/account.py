from django import forms

from ..models import Account, Profile

class AccountForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ('organization', 'street', 'payment_gateway', 'paypal_business',)

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ()
