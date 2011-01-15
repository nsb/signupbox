from django.db import models

class QuickPayTransaction(models.Model):
    amount = models.DecimalField(max_digits=7, decimal_places=2,)
    currency = models.CharField(max_length=3)
    time = models.DateTimeField()
    state = models.CharField(max_length=128)
    qpstat = models.CharField(max_length=128)
    qpstatmsg = models.CharField(max_length=512)
    merchant = models.CharField(max_length=512)
    merchantemail = models.EmailField(max_length=256)
    transaction = models.CharField(max_length=128)
    cardtype = models.CharField(max_length=128)
    cardnumber = models.CharField(max_length=128)
