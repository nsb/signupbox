from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

class Activity(models.Model):

    activity = models.CharField(max_length = 1028)
    timestamp = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.activity

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'
