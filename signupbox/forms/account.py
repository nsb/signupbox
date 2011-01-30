from django import forms
from django.utils.translation import ungettext, ugettext, ugettext_lazy as _

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

class InviteForm(forms.Form):
    email_adresses = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
    make_admins = forms.BooleanField(
        label = _("Make these users administrators?"),
        help_text = _("Administrators can invite new users and edit acocunt settings")
    )

class PermissionsForm(forms.Form):
    is_admin = forms.BooleanField(
        label=_('Account administrator'),
        required=False,
        help_text=_('Can invite new members and edit account settings'),
    )
