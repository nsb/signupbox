from django import forms

from ..models import Account, Profile

class AccountForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = (
            'organization',
            'street',
            'zip_code',
            'city',
            'country',
            'phone',
            'cvr',
            'payment_gateway',
            'paypal_business',
            'merchant_id',
            'secret_key',
        )

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ()
