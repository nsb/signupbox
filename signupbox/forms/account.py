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
    email_addresses = forms.CharField(
        help_text=_('Add email addresses for each person you wish to invite. Seperate each email address with a space.')
    )
    message = forms.CharField(widget=forms.Textarea)
    is_admin = forms.BooleanField(
        label = _("Make these users administrators?"),
        required = False,
        help_text = _("Administrators can invite new users and edit acocunt settings")
    )

    def clean_email_addresses(self):
        email_addresses = self.cleaned_data['email_addresses'].split(' ')
        f = forms.EmailField()
        return [f.clean(i) for i in email_addresses]

class PermissionsForm(forms.Form):
    is_admin = forms.BooleanField(
        label=_('Account administrator'),
        required=False,
        help_text=_('Can invite new members and edit account settings'),
    )

class InviteAcceptForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(label = _('Password'), widget = forms.PasswordInput)
    password2 = forms.CharField(label = _('Password (again)'), widget = forms.PasswordInput)

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('password', '') != cleaned_data.get('password2', ''):
            self._errors['password2'] = self.error_class(['Passwords must be the same.'])

        return cleaned_data
