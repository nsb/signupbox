from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from models import Account
from widgets import AccountWidget

class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.

    """
    accountname = forms.RegexField(
        regex=r'^\w+$', widget=AccountWidget, max_length=30, label=_(u'URL')
    )
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(maxlength=75)), label=_(u'email address'))
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_(u'password'))
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_(u'password (again)'))

    def clean_accountname(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        try:
            account = Account.objects.get(name__iexact=self.cleaned_data['accountname'])
        except Account.DoesNotExist:
            return self.cleaned_data['accountname']
        raise forms.ValidationError(_(u'This url is already taken. Please choose another.'))

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_(u'This email address is already in use. Please supply a different email address.'))
        self.cleaned_data['username'] = self.cleaned_data['email']
        return self.cleaned_data['email']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        if 'password' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_(u'You must type the same password each time'))
        return self.cleaned_data
