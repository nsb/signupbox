from django import forms
from django.conf import settings
from django.utils.hashcompat import md5_constructor

from models import QuickpayTransaction
from signals import payment_was_successfull

class QuickpayForm(forms.ModelForm):
    """
    """
    def __init__(self, *args, **kwargs):
        self.secret = kwargs.pop('secret')
        super(QuickpayForm, self).__init__(*args, **kwargs)

    protocol = forms.IntegerField(widget=forms.HiddenInput, required=False, initial=3)
    msgtype = forms.CharField(widget=forms.HiddenInput, initial='authorize',)
    language = forms.CharField(initial=settings.LANGUAGE_CODE, required=False, widget=forms.HiddenInput)
    autocapture = forms.IntegerField(initial=0, required=False, widget=forms.HiddenInput)
    cardtypelock = forms.CharField(
        widget=forms.HiddenInput,
        required=False,
        initial = "3d-jcb,3d-mastercard,3d-mastercard-dk,3d-visa,3d-visa-dk,american-express," \
                  "american-express-dk,dankort,diners,diners-dk,jcb,mastercard,mastercard-dk,visa,visa-dk"
    )
    ordernumber = forms.CharField(widget=forms.HiddenInput,)
    amount = forms.CharField(widget=forms.HiddenInput, initial=0)
    currency = forms.CharField(widget=forms.HiddenInput)
    merchant = forms.CharField(widget=forms.HiddenInput)
    continueurl = forms.URLField(widget=forms.HiddenInput, required=False)
    cancelurl = forms.URLField(widget=forms.HiddenInput, required=False)
    callbackurl = forms.URLField(required=False, widget=forms.HiddenInput)
    md5check = forms.CharField(widget=forms.HiddenInput)
    state = forms.IntegerField(widget=forms.HiddenInput)
    time = forms.CharField(widget=forms.HiddenInput, required=False)
    qpstat = forms.CharField(widget=forms.HiddenInput)
    qpstatmsg = forms.CharField(widget=forms.HiddenInput, required=False)
    chstat = forms.CharField(widget=forms.HiddenInput)
    chstatmsg = forms.CharField(widget=forms.HiddenInput, required=False)
    merchantemail = forms.EmailField(widget=forms.HiddenInput)
    cardtype = forms.CharField(widget=forms.HiddenInput)
    cardnumber = forms.CharField(widget=forms.HiddenInput, required=False)
    cardexpire = forms.CharField(widget=forms.HiddenInput, required=False)
    transaction = forms.CharField(widget=forms.HiddenInput)
    description = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean(self):

        md_input = ''.join((
            self.cleaned_data['msgtype'],
            self.cleaned_data['ordernumber'],
            self.cleaned_data['amount'],
            self.cleaned_data['currency'],
            self.cleaned_data['time'],
            str(self.cleaned_data['state']),
            self.cleaned_data['qpstat'],
            self.cleaned_data['qpstatmsg'],
            self.cleaned_data['chstat'],
            self.cleaned_data['chstatmsg'],
            self.cleaned_data['merchant'],
            self.cleaned_data['merchantemail'],
            self.cleaned_data['transaction'],
            self.cleaned_data['cardtype'],
            self.cleaned_data['cardnumber'],
            self.secret,
        ))
        valid = md5_constructor(md_input).hexdigest() == \
            self.cleaned_data['md5check'] and \
                self.cleaned_data['qpstat'] == '000'
        if not valid:
            raise forms.ValidationError('Invalid quickpay transaction')

        return self.cleaned_data

    def save(self, *args, **kwargs):
        ret = super(QuickpayForm, self).save(*args, **kwargs)
        payment_was_successfull.send(ret)
        return ret

    class Meta:
        model = QuickpayTransaction
