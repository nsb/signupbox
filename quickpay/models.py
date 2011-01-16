from django.db import models

class QuickpayTransaction(models.Model):
    msgtype = models.CharField(max_length=128)
    ordernumber = models.CharField(max_length=20)
    amount = models.PositiveIntegerField()
    currency = models.CharField(max_length=3)
    time = models.CharField(max_length=12)
    state = models.IntegerField()
    qpstat = models.CharField(max_length=3)
    qpstatmsg = models.CharField(max_length=512, blank=True)
    chstat = models.CharField(max_length=3)
    chstatmsg = models.CharField(max_length=512, blank=True)
    merchant = models.CharField(max_length=100)
    merchantemail = models.EmailField(max_length=256)
    transaction = models.CharField(max_length=32)
    cardtype = models.CharField(max_length=32, blank=True)
    cardnumber = models.CharField(max_length=32, blank=True)
    cardexpire = models.CharField(max_length=4, blank=True)

    def __unicode__(self):
        return self.ordernumber