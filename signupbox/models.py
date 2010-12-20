# -*- coding: utf-8 -*-

import uuid
from urlparse import urlparse

from django.db import models
from django.db.models import signals, Max, Sum
from django.utils.translation import ugettext, ugettext_lazy as _
from django.template import defaultfilters
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site

from constants import *

PAYMENT_GATEWAY_CHOICES = (
    ('quickpay', _('Quickpay')),
)

class Account(models.Model):
    """
    Account
    """
    name = models.CharField(max_length=255, verbose_name=_('Account name'))
    organization = models.CharField(max_length=1024, verbose_name=_('Company'), blank=True)
    street = models.CharField(max_length=255, verbose_name=_('Street'), blank=True)
    zip_code = models.CharField(max_length=255, verbose_name=_('Zip code'), blank=True)
    city = models.CharField(max_length=255, verbose_name=_('City'), blank=True)
    country = models.CharField(max_length=255, verbose_name=_('City'), blank=True)
    phone = models.CharField(max_length=32, verbose_name=_('Phone number'), blank=True)
    email = models.EmailField(verbose_name=_('Email address'), blank=True)
    cvr = models.CharField(max_length=32, verbose_name=_('CVR number'), blank=True)
    payment_gateway = models.CharField(
        max_length=255, blank=True, verbose_name=_('Payment gateway'), choices=PAYMENT_GATEWAY_CHOICES
    )
    merchant_id = models.CharField(max_length=255, verbose_name=_("PBS number"), blank=True)
    secret_key = models.CharField(max_length=255, verbose_name=_('Secret key'), blank=True)
    autocapture = models.BooleanField(
        verbose_name=_('Auto capture'), blank=True, help_text=_('Automatically capture payments'), default=False,
    )
    domain = models.URLField(blank=True, verbose_name=_('Domain')) 
    extra_info = models.TextField(
        verbose_name=_('Extra info'), blank=True, help_text=_('Extra info to be included in the registration email.')
    )
    terms = models.TextField(verbose_name=_('Terms and conditions'), blank=True)
    google_analytics = models.CharField(
        max_length=100, verbose_name=_('Google analytics'), blank=True, help_text=_('Enter your Google analytics tracker code to enable tracking.')
    )
    users = models.ManyToManyField(User, related_name='accounts', verbose_name=_('Users'),)
    groups = models.ManyToManyField(
        Group,
        related_name='groups',
        blank=True,
        help_text=_("In addition to the permissions manually assigned, this account will also get all permissions granted to each group it is in.")
    )
    account_permissions = models.ManyToManyField(Permission, verbose_name=_('account permissions'), blank=True)
    site = models.ForeignKey(Site, blank=True)

    def __unicode__(self):
        return self.name

    def domain_for_account(self, request=None):
        """
        find the domain for an accounts public site

        """
        if self.domain:
            return urlparse(self.domain).netloc.rstrip('/')
        else:
            p_host = request.get_host().partition(':') if request else ('', '', '')
            return u'%s.%s%s%s' % (self.name.lower(), Site.objects.get_current(), p_host[1], p_host[2])

    def save(self, *args, **kwargs):

        if not self.id:
            self.site = Site.objects.get_current()
        super(Account, self).save( *args, **kwargs)

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")

class Profile(models.Model):
    """
    Extends django.contrib.auth.model.User.
    Available via User.get_profile()
    """

    # This is the only required field
    user = models.ForeignKey(User, unique=True)

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

def create_profile(sender, instance, created, **kwargs):
    """ auto create a profile for the user """
    if created:
        Profile.objects.create(user=instance)
signals.post_save.connect(create_profile, sender=User)

EVENT_STATUS_CHOICES = (
    (EVENT_STATUS_OPEN, _('Open')),
    (EVENT_STATUS_CLOSED, _('Closed')),
)

CURRENCY_CHOICES = (
    (CURRENCY_DKK, _('dkk')),
    (CURRENCY_EUR, _('euros')),
)

RECURRING_CHOICES = (
    (RECURRING_NEVER, _('Not repeated')),
    (RECURRING_DAILY, _('Daily')),
    (RECURRING_WEEKDAYS, _('Weekly on weekdays')),
    (RECURRING_WEEKLY, _('Weekly')),
    (RECURRING_MONTHLY, _('Monthly')),
    (RECURRING_YEARLY, _('Yearly')),
)

RECURRING_INTERVAL_CHOICES = [(num, num) for num in range(1,31)]

RECURRING_BY_DATE = 0
RECURRING_BY_WEEKDAY = 1

RECURRING_MONTHLY_CHOICES = (
    (RECURRING_BY_DATE, _('day in month')),
    (RECURRING_BY_WEEKDAY, _('day in week')),
)

class RecurringWeeklyDay(models.Model):
    site = models.ForeignKey(Site)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=1)

    def __unicode__(self):
        return self.short_name

class Event(models.Model):
    """
    Event

    >>> account = Account.objects.create(name="myaccount")

    # Create events
    >>> event = Event.objects.create(account=account, title='my event', begin_date='2050-01-01', end_date='2050-01-01')
    >>> event2 = Event.objects.create(account=account, title='my event', begin_date='2050-01-01', end_date='2050-01-01')

    # make sure slug is unique
    >>> event.slug != event2.slug
    True
    """
    title = models.CharField(
        max_length=255, verbose_name=_('What'), help_text=_('The event title'),
    )
    slug = models.SlugField(max_length=255)

    account = models.ForeignKey(Account)

    description = models.TextField(blank=True, verbose_name=_('Description'))
    venue = models.CharField(max_length=1024, verbose_name=_('Where'), blank=True, help_text=_('The event venue'),)

    # date and time fields
    begin_date = models.DateField()
    end_date = models.DateField()
    begin_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)

    # recurring fields
    recurring = models.IntegerField(
        blank=True, choices=RECURRING_CHOICES, default=RECURRING_NEVER, verbose_name=_('repeated')
    )
    recurring_end_date = models.DateField(blank=True, null=True, verbose_name=_('ends'))

    # repeat only every interval. every three days or every fifth week...
    recurring_interval = models.IntegerField(
        choices=RECURRING_INTERVAL_CHOICES, blank=True, default=1, verbose_name=_('repeat every')
    )

    # only used for recurring weekly
    recurring_weekly_days = models.ManyToManyField(RecurringWeeklyDay, blank=True, null=True)

    # only used for recurring monthly
    recurring_monthly=models.IntegerField(blank=True, choices=RECURRING_MONTHLY_CHOICES, default=RECURRING_BY_DATE)

    capacity = models.IntegerField(
        default=0,
        verbose_name=_('Capacity'),
        help_text=_('0 for unlimited.')
    )
    status = models.CharField(
        max_length=32,
        verbose_name=_('Status'),
        choices=EVENT_STATUS_CHOICES,
        default='open',
        db_index=True
    )

    def save(self, *args, **kwargs):

        # auto create slug
        if not self.slug:
            slug = defaultfilters.slugify(self.title)
            i = 2
            while True:
                try:
                    Event.objects.get(slug__exact=slug)
                    slug = u'%s-%d' % (defaultfilters.slugify(self.title), i)
                    i += 1
                except Event.DoesNotExist:
                    break;
            self.slug = slug

        super(Event, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('event', (), {'account__name': self.account.name, 'id': self.id})

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['begin_date', 'begin_time', 'title', 'slug']
        unique_together = (('account', 'slug'),)

class Ticket(models.Model):
    event = models.ForeignKey(Event, related_name='tickets')
    name = models.CharField(max_length=1024)
    description = models.CharField(max_length=1024, blank=True)
    begin_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, blank=True, default='DKK')

    def __unicode__(self):
        return self.name

class Booking(models.Model):
    event = models.ForeignKey(Event, related_name='bookings')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    notes = models.CharField(max_length=255, blank=True, verbose_name=_('Notes'))
    description = models.CharField(max_length=1024, blank=True)
    ordernum = models.CharField(max_length=255)
    transaction = models.CharField(max_length=255, blank=True)
    cardtype = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0)
    currency = models.CharField(max_length=3, blank=True)
    confirmed = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s: #%s' % (self.event.title, self.id)

FIELD_TYPE_CHOICES = (
    (TEXT_FIELD, _('text')),
    (TEXTAREA_FIELD, _('multiline text')),
    (CHECKBOX_FIELD, _('checkbox')),
    (EMAIL_FIELD, _('email')),
    (SELECT_FIELD, _('select options')),
    (RADIOBUTTON_FIELD, _('radio buttons')),
    (PHONE_FIELD, _('phone')),
)

class Field(models.Model):
    """
    """
    event = models.ForeignKey(Event, related_name='fields')
    label = models.CharField(max_length=255, verbose_name=_('Label'))
    help_text = models.CharField(max_length=255, blank=True, verbose_name=_('Help text'))
    type = models.CharField(max_length=255, choices=FIELD_TYPE_CHOICES, verbose_name=_('Type'))
    required = models.BooleanField(default=False, verbose_name=_('Required'))
    in_extra = models.BooleanField(default=False, verbose_name=_('In extra forms'))
    ordering = models.IntegerField(blank=True)
    name = models.CharField(max_length=36, blank=True)

    def __unicode__(self):
        return self.label

    def save(self, *args, **kwargs):

        if not self.name:
            self.name = uuid.uuid4()

        if not self.ordering:
            self.ordering = Field.objects.filter(event=self.event).aggregate(Max('ordering'))['ordering__max'] or 0 + 1

        super(Field, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('event', 'name')
        ordering = ('id',)

class AttendeeManager(models.Manager):
    def confirmed(self, event=None):
        qs = self.filter(booking__event=event) if event else self.all()
        return qs.filter(status=ATTENDEE_CONFIRMED, booking__confirmed=True)

    def unconfirmed(self, event=None):
        qs = self.filter(booking__event=event) if event else self.all()
        return self.filter(status=ATTENDEE_UNCONFIRMED, booking__confirmed=True)

    def cancelled(self, event=None):
        qs = self.filter(booking__event=event) if event else self.all()
        return self.filter(status=ATTENDEE_CANCELLED, booking__confirmed=True)

ATTENDEE_STATUS_CHOICES = (
    ( ATTENDEE_CONFIRMED, _('Confirmed')),
    ( ATTENDEE_UNCONFIRMED, _('Unconfirmed')),
    ( ATTENDEE_CANCELLED, _('Cancelled')),
)

class Attendee(models.Model):
    booking = models.ForeignKey(Booking, related_name='attendees')
    ticket = models.ForeignKey(Ticket, related_name='attendees')
    status = models.CharField(
        max_length=32,
        choices=ATTENDEE_STATUS_CHOICES,
        default=ATTENDEE_CONFIRMED,
    )
    fields = models.ManyToManyField(Field, through="FieldValue")

    objects = AttendeeManager()

    def __unicode__(self):
        return self.display_value

class FieldValue(models.Model):
    """
    """
    attendee = models.ForeignKey(Attendee, related_name='values')
    field = models.ForeignKey(Field)
    value = models.CharField(max_length=1024, blank=True)

    def __unicode__(self):
        return u'%s:%s' % (self.field, self.value)

    class Meta:
        ordering = ('field',)

class FieldOption(models.Model):
    """
    """

    field = models.ForeignKey(Field, related_name='options')
    value = models.CharField(max_length=512, verbose_name='')

    def __unicode__(self):
        return self.value

    class Meta:
        ordering = ('id',)

def create_default_fields(sender, instance, created, **kwargs):
    default_fields = (
        {'label':ugettext('Name'), 'type':TEXT_FIELD, 'required':True, 'in_extra':True,},
        {'label':ugettext('Organization'), 'type':TEXT_FIELD,},
        {'label':ugettext('Email'), 'type':EMAIL_FIELD, 'required':True, 'in_extra':True,},
        {'label':ugettext('Street'), 'type':TEXT_FIELD,},
        {'label':ugettext('Zip code'), 'type':TEXT_FIELD,},
        {'label':ugettext('City'), 'type':TEXT_FIELD,},
        {'label':ugettext('Country'), 'type':TEXT_FIELD,},
        {'label':ugettext('Phone number'), 'type':PHONE_FIELD,},
    )
    if created:
        for index, field in enumerate(default_fields):
            Field.objects.create(event=instance, **field)

# auto create default form fields
signals.post_save.connect(create_default_fields, sender=Event)

def create_default_tickets(sender, instance, created, **kwargs):
    default_tickets = (
        {'name':ugettext('Default ticket'),},
    )
    if created:
        for index, ticket in enumerate(default_tickets):
            Ticket.objects.create(event=instance, **ticket)

# auto create default tickets
signals.post_save.connect(create_default_tickets, sender=Event)
