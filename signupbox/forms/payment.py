from django import forms
from django.conf import settings

class QuickPayForm(forms.Form):
    """
    """

    #protocol = 3
    #msgtype = 'authorize'
    #language = settings.LANGUAGE_CODE
    #autocapture = 1 if self.event.account.autocapture else 0
    #cardtypelock = \
        #"3d-jcb,3d-mastercard,3d-mastercard-dk,3d-visa,3d-visa-dk,american-express," \
        #"american-express-dk,dankort,diners,diners-dk,jcb,mastercard,mastercard-dk,visa,visa-dk"
    #amount = int(self.total_price * 100)
    #currency = self.event.currency
    #merchant = self.event.account.merchant_id
    #continueurl = 'http://%s%s?%s' % (
        #request.get_host(),
        #reverse('register_complete', kwargs={'slug':self.event.slug}),
        #request.GET.urlencode()
    #)
    #cancelurl = 'http://%s%s?%s' % (
        #request.get_host(),
        #reverse('register_incomplete', kwargs={'slug':self.event.slug}),
        #request.GET.urlencode()
    #)
    #callbackurl = 'http://%s%s?%s' % (
        #request.get_host(),
        #reverse('register_register', kwargs={'slug':self.event.slug}),
        #request.GET.urlencode()
    #)
    #md_input = ''.join(
        #(str(protocol),
          #msgtype,
          #merchant,
          #language,
          #ordernumber,
          #str(amount),
          #currency,
          #continueurl,
          #cancelurl,
          #callbackurl,
          #str(autocapture),
          #cardtypelock,
          #self.event.account.secret_key.strip())
      #)
    #md5check = md5_constructor(md_input).hexdigest().lower()

    #self.initial = {
        #'protocol':str(protocol),
        #'msgtype':msgtype,
        #'merchant':merchant,
        #'language':language,
        #'ordernumber':ordernumber,
        #'amount':str(amount),
        #'currency':currency,
        #'continueurl':continueurl,
        #'cancelurl':cancelurl,
        #'callbackurl':callbackurl,
        #'autocapture':str(autocapture),
        #'cardtypelock':cardtypelock,
        #'md5check':md5check
    #}


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
    cardtypelock = forms.CharField(widget=forms.HiddenInput, required=False)
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

class PaypalForm(forms.Form):
    cmd = forms.CharField(initial="_xclick", widget=forms.HiddenInput)
    business = forms.EmailField(widget=forms.HiddenInput)
    lc = forms.CharField(initial="US", widget=forms.HiddenInput)
    item_name = forms.CharField(widget=forms.HiddenInput)
    item_number = forms.CharField(widget=forms.HiddenInput)
    amount = forms.CharField(widget=forms.HiddenInput)
    currency_code = forms.CharField(initial="USD", widget=forms.HiddenInput)
    button_subtype = forms.CharField(initial="services", widget=forms.HiddenInput)
    no_note = forms.IntegerField(initial=0, widget=forms.HiddenInput)
    bn = forms.CharField(initial="No_Value", widget=forms.HiddenInput)
    notify_url = forms.CharField(widget=forms.HiddenInput)
    cancel_return = forms.CharField(widget=forms.HiddenInput())
    return_url = forms.CharField(widget=forms.HiddenInput(attrs={"name":"return"}))
