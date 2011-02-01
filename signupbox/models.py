# -*- coding: utf-8 -*-

from datetime import datetime
import uuid, re
from urlparse import urlparse

from django.db import models
from django.db.models import signals, Max, Sum
from django.utils.translation import ugettext, ugettext_lazy as _
from django.template import defaultfilters
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.template import defaultfilters
from django.contrib.contenttypes.models import ContentType

from objperms.models import ObjectPermission

from paypal.standard.ipn.signals import payment_was_successful
from quickpay.signals import payment_was_successfull as quickpay_payment_was_successfull
from activities.models import Activity

from constants import *
from signals import booking_confirmed
from tasks import process_booking

PAYMENT_GATEWAY_CHOICES = (
    ('paypal', _('PayPal')),
    ('quickpay', _('Quickpay')),
)

class AccountManager(models.Manager):
    def by_request(self, request):

        account = None
        #strip port number
        host = request.get_host().partition(':')[0]
        domain = Site.objects.get_current().domain

        try:
            account = self.get(domain=u'http://%s/' % host)
        except Account.DoesNotExist:
            m = re.match('(?P<account_name>[\w]+)\.%s' % domain, host, re.IGNORECASE)
            if m:
                try:
                    account = self.get(name__iexact=m.group('account_name'))
                except Account.DoesNotExist:
                    pass
        return account


class Account(models.Model):
    """
    Account
    """
    name = models.CharField(max_length=255, verbose_name=_('Account name'))
    organization = models.CharField(max_length=1024, verbose_name=_('Company'), blank=True)
    street = models.CharField(max_length=255, verbose_name=_('Street'), blank=True)
    zip_code = models.CharField(max_length=255, verbose_name=_('Zip code'), blank=True)
    city = models.CharField(max_length=255, verbose_name=_('City'), blank=True)
    country = models.CharField(max_length=255, verbose_name=_('Country'), blank=True)
    phone = models.CharField(max_length=32, verbose_name=_('Phone number'), blank=True)
    email = models.EmailField(verbose_name=_('Email address'), blank=True)
    cvr = models.CharField(max_length=32, verbose_name=_('CVR number'), blank=True)
    payment_gateway = models.CharField(
        max_length=255, blank=True, verbose_name=_('Payment gateway'), choices=PAYMENT_GATEWAY_CHOICES
    )
    merchant_id = models.CharField(max_length=255, verbose_name=_("PBS number"), blank=True)
    secret_key = models.CharField(max_length=255, verbose_name=_('Secret key'), blank=True)
    paypal_business = models.CharField(max_length=255, blank=True)
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
    site = models.ForeignKey(Site, blank=True)

    objects = AccountManager()

    def __unicode__(self):
        return self.name

    @property
    def activities(self):
        return Activity.objects.filter(object_id__in=self.events.values_list('id', flat=True))

    @property
    def display_name(self):
        return self.organization or self.name

    def set_admin_status(self, user, is_admin):
        perm, created = ObjectPermission.objects.get_or_create(
            user=user,
            object_id=self.pk,
            content_type=ContentType.objects.get_for_model(self)
        )
        perm.can_view = is_admin
        perm.can_change = is_admin
        perm.save()

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

class EventManager(models.Manager):
    def upcoming(self):
        return self.filter(begins__gt=datetime.now())

    def previous(self):
        return self.filter(begins__lt=datetime.now())

class Event(models.Model):
    """
    Event

    >>> account = Account.objects.create(name="myaccount")

    # Create events
    >>> event = Event.objects.create(account=account, title='my event', begins='2050-01-01', ends='2050-01-01')
    >>> event2 = Event.objects.create(account=account, title='my event', begins='2050-01-01', ends='2050-01-01')

    # make sure slug is unique
    >>> event.slug != event2.slug
    True
    """
    title = models.CharField(
        max_length=255, verbose_name=_('What'), help_text=_('The event title'),
    )
    slug = models.SlugField(max_length=255)

    account = models.ForeignKey(Account, related_name='events')

    description = models.TextField(blank=True, verbose_name=_('Description'))
    venue = models.CharField(max_length=1024, verbose_name=_('Where'), blank=True, help_text=_('The event venue'),)

    # date and time fields
    begins = models.DateTimeField()
    ends = models.DateTimeField()

    capacity = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Capacity'),
        help_text=_('Leave blank for unlimited.')
    )
    status = models.CharField(
        max_length=32,
        verbose_name=_('Status'),
        choices=EVENT_STATUS_CHOICES,
        default='open',
        db_index=True
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, blank=True, default='DKK')

    activities = generic.GenericRelation(Activity)

    objects = EventManager()

    @property
    def confirmed_attendees(self):
        return Attendee.objects.confirmed(event=self)

    @property
    def website(self):
        return ''.join(('http://', self.account.domain_for_account(), '/', self.slug, '/'))

    @property
    def has_payments(self):
        return self.tickets.filter(price__gt=0).exists()

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
        ordering = ['begins', 'title', 'slug']
        unique_together = (('account', 'slug'),)

class Ticket(models.Model):
    event = models.ForeignKey(Event, related_name='tickets')
    name = models.CharField(max_length=1024)
    description = models.CharField(max_length=1024, blank=True)
    offered_from = models.DateField(blank=True, null=True)
    offered_to = models.DateField(blank=True, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    def __unicode__(self):
        return self.name

class Booking(models.Model):
    event = models.ForeignKey(Event, related_name='bookings')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    notes = models.TextField(blank=True)
    description = models.CharField(max_length=1024, blank=True)
    transaction = models.CharField(max_length=255, blank=True)
    cardtype = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0)
    currency = models.CharField(max_length=3, blank=True)
    confirmed = models.BooleanField(default=False)

    @property
    def activity(self):
        count = self.attendees.count()
        attendees = [attendee.display_value for attendee in self.attendees.all()]
        if count == 0:
            return ''
        elif count == 1:
            ret = attendees[0]
        else:
            ret = ugettext('%s and %s' % (', '.join(attendees[:-1]), attendees[-1]))
        ret = ret + ugettext(' registered for %s.' % self.event.title)
        return ret

    @property
    def ordernumber(self):
        return str(self.pk)

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
    event = models.ForeignKey(Event, related_name='fields', null=True)
    label = models.CharField(max_length=255, verbose_name=_('Label'))
    help_text = models.CharField(max_length=255, blank=True, verbose_name=_('Help text'))
    type = models.CharField(max_length=255, choices=FIELD_TYPE_CHOICES, verbose_name=_('Type'), default=TEXT_FIELD)
    required = models.BooleanField(default=False, verbose_name=_('Required'))
    in_extra = models.BooleanField(default=False, verbose_name=_('In extra forms'))
    ordering = models.IntegerField()
    name = models.CharField(max_length=36, blank=True)

    def __unicode__(self):
        return self.label

    def save(self, *args, **kwargs):

        if not self.name:
            self.name = uuid.uuid4()

        if not self.ordering:
            self.ordering = (Field.objects.filter(event=self.event).aggregate(Max('ordering'))['ordering__max'] or 0) + 1

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

    def get_query_set(self):
        """
        add display_label, display_value and email attributes to attendee queryset objects

        """
        return super(AttendeeManager, self).get_query_set().extra(
            select={
                'display_label':
                """
                SELECT label from signupbox_fieldvalue, signupbox_field WHERE
                signupbox_fieldvalue.attendee_id = signupbox_attendee.id AND
                signupbox_fieldvalue.field_id = signupbox_field.id AND
                signupbox_field.ordering = 1
                """,
                'display_value':
                """
                SELECT value from signupbox_fieldvalue, signupbox_field WHERE
                signupbox_fieldvalue.attendee_id = signupbox_attendee.id AND
                signupbox_fieldvalue.field_id = signupbox_field.id AND
                signupbox_field.ordering = 1
                """,
                'email':
                """
                SELECT value from signupbox_fieldvalue, signupbox_field WHERE
                signupbox_fieldvalue.attendee_id = signupbox_attendee.id AND
                signupbox_fieldvalue.field_id = signupbox_field.id AND
                signupbox_field.type = '%s'
                """ % EMAIL_FIELD
            }
        )

ATTENDEE_STATUS_CHOICES = (
    ( ATTENDEE_CONFIRMED, _('Confirmed')),
    ( ATTENDEE_UNCONFIRMED, _('Unconfirmed')),
    ( ATTENDEE_CANCELLED, _('Cancelled')),
)

class Attendee(models.Model):
    account = models.ForeignKey(Account, related_name='attendees')
    booking = models.ForeignKey(Booking, related_name='attendees')
    ticket = models.ForeignKey(Ticket, related_name='attendees')
    status = models.CharField(
        max_length=32,
        choices=ATTENDEE_STATUS_CHOICES,
        default=ATTENDEE_CONFIRMED,
    )
    fields = models.ManyToManyField(Field, through="FieldValue")

    objects = AttendeeManager()

    def save(self, *args, **kwargs):

        if self.booking:
            self.account = self.booking.event.account
        super(Attendee, self).save( *args, **kwargs)

    def __unicode__(self):
        try:
            return self.display_value
        except ValueError:
            try:
                return self.values.all()[0].value
            except KeyError:
                return ''

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

def on_paypal_payment_success(sender, **kwargs):
    ipn_obj = sender
    booking_confirmed.send(sender=ipn_obj, booking_id=int(ipn_obj.item_number))
payment_was_successful.connect(on_paypal_payment_success)

def on_quickpay_payment_success(sender, **kwargs):
    transaction = sender
    booking = Booking.objects.get(pk=int(transaction.ordernumber.lstrip('0')))
    booking_confirmed.send(sender=transaction, booking_id=booking.id)
quickpay_payment_was_successfull.connect(on_quickpay_payment_success)

def on_booking_confirmed(sender, booking_id, **kwargs):

    booking = Booking.objects.get(pk=booking_id)
    booking.confirmed = True
    booking.save()

    process_booking.delay(booking)

booking_confirmed.connect(on_booking_confirmed)
