from django import forms
from django.conf import settings

class QuickpayForm(forms.Form):
    """
    """

    #md_input = ''.join(
        #(form.cleaned_data['msgtype'],
          #form.cleaned_data['ordernumber'],
          #form.cleaned_data['amount'],
          #form.cleaned_data['currency'],
          #form.cleaned_data['time'],
          #form.cleaned_data['state'],
          #form.cleaned_data['qpstat'],
          #form.cleaned_data['qpstatmsg'],
          #form.cleaned_data['chstat'],
          #form.cleaned_data['chstatmsg'],
          #form.cleaned_data['merchant'],
          #form.cleaned_data['merchantemail'],
          #form.cleaned_data['transaction'],
          #form.cleaned_data['cardtype'],
          #form.cleaned_data['cardnumber'],
          #self.event.account.secret_key.strip())
    #)
    #self.valid = md5_constructor(md_input).hexdigest() == \
        #form.cleaned_data['md5check'] and \
            #form.cleaned_data['qpstat'] == '000'


    protocol = forms.IntegerField(widget=forms.HiddenInput, required=False, initial=3)
    msgtype = forms.CharField(widget=forms.HiddenInput, required=False, initial='authorize',)
    language = forms.CharField(initial=settings.LANGUAGE_CODE, required=False, widget=forms.HiddenInput)
    autocapture = forms.IntegerField(initial=0, required=False, widget=forms.HiddenInput)
    cardtypelock = forms.CharField(
        widget=forms.HiddenInput,
        required=False,
        initial = "3d-jcb,3d-mastercard,3d-mastercard-dk,3d-visa,3d-visa-dk,american-express," \
                  "american-express-dk,dankort,diners,diners-dk,jcb,mastercard,mastercard-dk,visa,visa-dk"
    )
    ordernumber = forms.CharField(widget=forms.HiddenInput, required=False)
    amount = forms.CharField(widget=forms.HiddenInput, required=False, initial=0)
    currency = forms.CharField(widget=forms.HiddenInput, required=False)
    merchant = forms.CharField(widget=forms.HiddenInput, required=False)
    continueurl = forms.URLField(widget=forms.HiddenInput, required=False)
    cancelurl = forms.URLField(widget=forms.HiddenInput, required=False)
    callbackurl = forms.URLField(required=False, widget=forms.HiddenInput)
    md5check = forms.CharField(widget=forms.HiddenInput, required=False)
    state = forms.CharField(widget=forms.HiddenInput, required=False)
    time = forms.CharField(widget=forms.HiddenInput, required=False)
    qpstat = forms.CharField(widget=forms.HiddenInput, required=False)
    qpstatmsg = forms.CharField(widget=forms.HiddenInput, required=False)
    chstat = forms.CharField(widget=forms.HiddenInput, required=False)
    chstatmsg = forms.CharField(widget=forms.HiddenInput, required=False)
    merchantemail = forms.EmailField(widget=forms.HiddenInput, required=False)
    cardtype = forms.CharField(widget=forms.HiddenInput, required=False)
    cardnumber = forms.CharField(widget=forms.HiddenInput, required=False)
    transaction = forms.CharField(widget=forms.HiddenInput, required=False)
    description = forms.CharField(widget=forms.HiddenInput, required=False)
