# -*- coding: utf-8 -*-

from datetime import datetime, date, time, timedelta
import uuid, re
from urlparse import urlparse
from random import random, SystemRandom
import string

from django.db import models
from django.db.models import signals, Max, Sum
from django.utils.translation import ugettext, ugettext_lazy as _
from django.template import defaultfilters
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.template import defaultfilters
from django.contrib.contenttypes.models import ContentType
from django.utils.hashcompat import sha_constructor
from django.core.urlresolvers import reverse

from objperms.models import ObjectPermission

from paypal.standard.ipn.signals import payment_was_successful
from quickpay.signals import payment_was_successfull as quickpay_payment_was_successfull
from activities.models import Activity

from constants import *
from signals import booking_confirmed

PAYMENT_GATEWAY_CHOICES = (
    ('paypal', _('PayPal')),
    ('quickpay', _('Quickpay')),
)

SMS_GATEWAY_CHOICES = (
    ('nexmo', _('Nexmo')),
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
                    account = self.get(name__iexact=m.group('account_name'),
                        site=Site.objects.get_current())
                except Account.DoesNotExist:
                    pass
        return account


class Account(models.Model):
    """
    Account
    """
    name = models.CharField(max_length=255, verbose_name=_('Account name'))
    organization = models.CharField(max_length=1024, verbose_name=_('Company'), blank=True)
    genitive_organization = models.CharField(max_length=255,
                                     verbose_name=_('Genitive organization name'),
                                     blank=True,
                                     help_text=_('Organization name in genitive form.'))
    street = models.CharField(max_length=255, verbose_name=_('Street'), blank=True)
    zip_code = models.CharField(max_length=255, verbose_name=_('Zip code'), blank=True)
    city = models.CharField(max_length=255, verbose_name=_('City'), blank=True)
    country = models.CharField(max_length=255, verbose_name=_('Country'), blank=True)
    phone = models.CharField(max_length=32, verbose_name=_('Phone number'), blank=True)
    email = models.EmailField(verbose_name=_('Email address'), blank=True)
    cvr = models.CharField(max_length=32, verbose_name=_('CVR number'), blank=True)
    payment_gateway = models.CharField(max_length=255, blank=True,
        verbose_name=_('Payment gateway'), choices=PAYMENT_GATEWAY_CHOICES)
    merchant_id = models.CharField(max_length=255, verbose_name=_("PBS number"), blank=True)
    secret_key = models.CharField(max_length=255, verbose_name=_('Secret key'), blank=True)
    paypal_business = models.CharField(max_length=255, blank=True)
    autocapture = models.BooleanField(verbose_name=_('Auto capture'),
        blank=True, help_text=_('Automatically capture payments'), default=False)
    sms_gateway = models.CharField(max_length=255, blank=True,
        verbose_name=_('SMS gateway'), choices=SMS_GATEWAY_CHOICES)
    sms_gateway_username = models.CharField(max_length=255, verbose_name=_("SMS gateway username"), blank=True)
    sms_gateway_password = models.CharField(max_length=255, verbose_name=_('SMS gateway password'), blank=True)
    domain = models.URLField(blank=True, verbose_name=_('Domain'))
    extra_info = models.TextField(verbose_name=_('Extra info'), blank=True,
        help_text=_('Extra info to be included in the registration email.'))
    terms = models.TextField(verbose_name=_('Terms and conditions'), blank=True)
    google_analytics = models.CharField(max_length=100, verbose_name=_('Google analytics'),
        blank=True, help_text=_('Enter your Google analytics tracker code to enable tracking.'))
    script_codes = models.TextField(verbose_name=_('Script codes'), blank=True,
                                    help_text=_('Script codes that will added on all public event pages.'))
    users = models.ManyToManyField(User, related_name='accounts', verbose_name=_('Users'),)
    groups = models.ManyToManyField(Group, related_name='groups', blank=True,
        help_text=_("""In addition to the permissions manually assigned,
            this account will also get all permissions granted to each group it is in."""))
    relationwise_survey_id = models.CharField(
        max_length=128,
        blank=True,
        verbose_name=_('Relationwise Survey Id'),
        help_text=_('Required in order to use the Relationwise integration.'))
    reply_to = models.EmailField(max_length=254,
                                 blank=True,
                                 verbose_name=_('Reply to'),
                                 help_text=_('The default reply-to email address for all outgoing emails.'))
    from_address = models.EmailField(max_length=254,
                                     blank=True,
                                     verbose_name=_('From address'),
                                     help_text=_('The default from email address for all outgoing emails.'))


    site = models.ForeignKey(Site)

    objects = AccountManager()

    def __unicode__(self):
        return self.name

    @property
    def activities(self):
        return Activity.objects.filter(
            object_id__in=self.events.values_list('id', flat=True))

    @property
    def activities_short_list(self, count=6):
        return self.activities.all()[:count]

    @property
    def display_name(self):
        return self.organization or self.name

    @property
    def genitive_display_name(self):
        return self.genitive_organization or self.display_name

    def set_perms(self, user, view=None, change=None, delete=None):
        perm, created = ObjectPermission.objects.get_or_create(user=user,
            object_id=self.pk, content_type=ContentType.objects.get_for_model(self))
        if view is not None:
            perm.can_view = view
        if change is not None:
            perm.can_change = change
        if delete is not None:
            perm.can_delete = delete
        perm.save()

    def remove_user(self, user):
        self.set_perms(user, view=False, change=False, delete=False)
        self.users.remove(user)

    def domain_for_account(self, request=None):
        """
        find the domain for an accounts public site

        """
        if self.domain:
            return urlparse(self.domain).netloc.rstrip('/')
        else:
            p_host = request.get_host().partition(':') if request else ('', '', '')
            return u'%s.%s%s%s' % (self.name.lower(),
                Site.objects.get_current(), p_host[1], p_host[2])

    def save(self, *args, **kwargs):

        if not self.id:
            self.site = Site.objects.get_current()
        if not self.genitive_organization:
            self.genitive_organization = self.organization
        super(Account, self).save( *args, **kwargs)

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")

class AccountInviteManager(models.Manager):
    def get_query_set(self):
        return super(AccountInviteManager, self).get_query_set().filter(
            is_accepted=False, expires__gt=datetime.now()
        )

class AccountInvite(models.Model):
    account = models.ForeignKey(Account, related_name='invites')
    key = models.CharField(max_length=40)
    email = models.EmailField(max_length=128)
    is_admin = models.BooleanField()
    is_accepted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField()
    invited_by = models.ForeignKey(User)

    objects = AccountInviteManager()

    def __unicode__(self):
        return self.email

    @models.permalink
    def get_absolute_url(self):
        return ('signupbox.views.account_invitation', [self.key,])

    def url(self):
        return '%s%s' % (Site.objects.get_current().domain, self.get_absolute_url())

    def _create_key(self):
        salt = sha_constructor(str(random())).hexdigest()[:5]
        key = sha_constructor("%s%s%s" % (datetime.now(), salt, self.email)).hexdigest()
        return key

    def save(self, *args, **kwargs):

        if not self.key:
            self.key = self._create_key()

        if not self.expires:
            self.expires = datetime.now() + timedelta(days=7)

        super(AccountInvite, self).save(*args, **kwargs)


class RelationWiseSurvey(models.Model):
    account = models.ForeignKey(Account, related_name='surveys')
    survey_id = models.CharField(max_length=128)
    name = models.CharField(max_length=256)
    subject = models.CharField(max_length=1024, verbose_name=_('subject'))
    message = models.TextField(verbose_name=_('email'))
    language_parameter = models.CharField(max_length=32, blank=True,
                                          verbose_name=_('Language parameter'))

    def __unicode__(self):
        return self.name


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
    (CURRENCY_DKK, _('kr.')),
    (CURRENCY_EUR, _('euros')),
)

LANGUAGE_CHOICES = (
    ('da', _('Danish')),
    ('en', _('English')),
)

SEND_REMINDER_CHOICES = (
    (0, _('Never')),
    (1, _('1 Day')),
    (3, _('Three days')),
    (7, _('One week')),
    (14, _('Two weeks')),
    (30, _('One month')),
)

class EventManager(models.Manager):

    def get_query_set(self):
        qs = super(EventManager, self).get_query_set()

        confirmed_attendees_query = (
            'select coalesce(sum(attendee_count), 0) from signupbox_attendee, signupbox_booking '
            'WHERE signupbox_attendee.status = \'%s\' and '
            'signupbox_booking.confirmed = True and '
            'signupbox_event.id = signupbox_booking.event_id and '
            'signupbox_booking.id = signupbox_attendee.booking_id') % ATTENDEE_CONFIRMED

        extra_selects = {
            'confirmed_attendees_count': confirmed_attendees_query,
        }

        return qs.extra(select=extra_selects)

    def upcoming(self):
        return self.filter(begins__gt=datetime.now())

    def previous(self):
        return self.filter(begins__lt=datetime.now()).exclude(archived=True).order_by('-begins')

    def archived(self):
        return self.filter(begins__lt=datetime.now(), archived=True).order_by('-begins')

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
    project_id = models.CharField(max_length=128,
                                  blank=True,
                                  verbose_name=_('Project Id'),
                                  help_text=_('Add the project id that '
                                              'payments should be transfered '
                                              'to.'))

    account = models.ForeignKey(Account, related_name='events')

    description = models.TextField(blank=True, verbose_name=_('Description'))
    venue = models.CharField(max_length=1024,
        verbose_name=_('Where'), blank=True, help_text=_('The event venue'),)
    address = models.CharField(max_length=255, blank=True, verbose_name=_('Street'))
    city = models.CharField(max_length=255, blank=True, verbose_name=_('City'))
    zip_code = models.CharField(max_length=255, blank=True, verbose_name=_('Zip code'))

    # date and time fields
    begins = models.DateTimeField(verbose_name=_('Begins'), db_index=True)
    ends = models.DateTimeField(verbose_name=_('Ends'))

    capacity = models.IntegerField(blank=True, null=True,
        verbose_name=_('Capacity'), help_text=_('Leave blank for unlimited.'))
    status = models.CharField(max_length=32, verbose_name=_('Status'),
        choices=EVENT_STATUS_CHOICES, default='open', db_index=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES,
        blank=True, default='DKK', verbose_name=_('Currency'))

    send_reminder = models.PositiveIntegerField(default=0, choices=SEND_REMINDER_CHOICES,
        verbose_name=_('Send reminder'), help_text=_('When should the reminder be sent?'))
    reminder_subject = models.CharField(max_length=2048, verbose_name=_('Reminder subject'), blank=True)
    reminder = models.TextField(blank=True, verbose_name=_('Reminder'))
    reminders_sent = models.DateTimeField(blank=True, null=True)

    activities = generic.GenericRelation(Activity)

    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='da', verbose_name=_('Language'))
    survey = models.ForeignKey(RelationWiseSurvey, null=True, blank=True, related_name='events', on_delete=models.SET_NULL)
    surveyEnabled = models.BooleanField(default=False,
                                        verbose_name=_('Survey'),
                                        help_text=_('Send out survey questions to attendees after the event?'))
    surveySent = models.BooleanField(default=False)
    subscribers = models.ManyToManyField(User, related_name='events',
                                         verbose_name=_('Subscribers'))
    archived = models.BooleanField(default=False, db_index=True)
    show_newsletter_subscribe = models.BooleanField(default=True,
                                                    verbose_name=_('Show newsletter signup'),
                                                    help_text=_('Show newsletter signup after registration?'))
    extra_info_override = models.TextField(verbose_name=_('Extra info'),
                                           blank=True,
                                           help_text=_('Replaces default extra info in the registration email.'))
    show_address = models.BooleanField(default=True,
                                       verbose_name=_('Show address'),
                                       help_text=_('Show address in emails and public pages'))
    redirect_public_page_url = models.URLField(blank=True,
                                               verbose_name=_('redirect event page'),
                                               help_text=_('redirect event page to this URL.')
                                               )

    objects = EventManager()

    @property
    def is_open(self):
        return self.status == EVENT_STATUS_OPEN and \
            (self.confirmed_attendees_count < self.capacity if self.capacity else True) and \
                self.begins > datetime.now() and self.tickets_available.exists()

    @property
    def has_extra_forms(self):
        return self.fields.filter(in_extra=True).exists()

    @property
    def confirmed_attendees(self):
        return Attendee.objects.confirmed(event=self)

    @property
    def website(self):
        return ''.join(('http://', self.account.domain_for_account(), '/', self.slug, '/'))

    @property
    def has_payments(self):
        return self.tickets.filter(price__gt=0).exists()

    @property
    def terms_url(self):
        return reverse('event_terms', kwargs={'slug':self.slug})

    @property
    def tickets_available(self):

        tickets = [ticket.pk for ticket in self.tickets.all() if not ticket.available or ticket.confirmed_attendee_count < ticket.available]
        return Ticket.objects.exclude(offered_from__gt=date.today()).exclude(offered_to__lt=date.today()).filter(pk__in=tickets)

    @property
    def activities(self):
        return Activity.objects.filter(object_id=self.pk)

    @property
    def activities_short_list(self, count=6):
        return self.activities.all()[:count]

    def save(self, *args, **kwargs):

        # auto create slug
        if not self.slug:
            slug = defaultfilters.slugify(self.title)
            i = 2
            while True:
                try:
                    Event.objects.get(slug__exact=slug, account=self.account)
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
    available = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Available'), help_text=_('Number of available tickets. Leave blank for event capacity.'))

    @property
    def confirmed_attendees(self):
        return self.attendees.filter(status=ATTENDEE_CONFIRMED, booking__confirmed=True)

    @property
    def confirmed_attendee_count(self):
        return self.confirmed_attendees.aggregate(Sum('attendee_count'))['attendee_count__sum'] or 0

    def __unicode__(self):
        return self.name

class BookingManager(models.Manager):
    def today(self):
        return self.filter(timestamp__range=(datetime.combine(
            date.today(), time.min), datetime.combine(date.today(), time.max)))

class Booking(models.Model):
    event = models.ForeignKey(Event, related_name='bookings')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    notes = models.TextField(blank=True)
    description = models.CharField(max_length=1024, blank=True)
    transaction = models.CharField(max_length=255, blank=True)
    cardtype = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, blank=True)
    confirmed = models.BooleanField(default=False)
    ordernumber = models.CharField(max_length=20)
    token = models.CharField(max_length=64, db_index=True, null=True)

    objects = BookingManager()

    @property
    def activity(self):
        count = self.attendees.count()
        attendees = [attendee.display_value for attendee in self.attendees.all()]
        if count == 0:
            return ''
        elif count == 1:
            attendee_names = ''.join(attendees)
        else:
            attendee_names = ugettext('%(attendee1)s and %(attendee2)s') % {
                'attendee1': ', '.join(attendees[:-1]), 'attendee2': attendees[-1]}

        return ugettext('%(name)s registered for %(event)s.') % {
            'name': attendee_names, 'event': self.event.title}

    def save(self, *args, **kwargs):
        """
        get ordernumber from database sequence

        """
        if not self.token:
            gen = SystemRandom()
            self.token = ''.join(gen.choice(string.ascii_lowercase + string.digits) for x in range(64))

        if not self.ordernumber:
            from django.db import connection
            cursor = connection.cursor()

            cursor.execute("SELECT nextval('booking_ordernum_seq')")
            (ordernum,) = cursor.fetchone()
            self.ordernumber = str(ordernum)

        return super(Booking, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%(title)s: #%(id)s' % {'title':self.event.title, 'id':self.id}

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
    type = models.CharField(max_length=255,
        choices=FIELD_TYPE_CHOICES, verbose_name=_('Type'), default=TEXT_FIELD)
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
            self.ordering = (Field.objects.filter(
                event=self.event).aggregate(Max('ordering'))['ordering__max'] or 0) + 1

        super(Field, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('event', 'name')
        ordering = ('ordering', 'id')

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
                'name':
                """
                SELECT value from signupbox_fieldvalue, signupbox_field WHERE
                signupbox_fieldvalue.attendee_id = signupbox_attendee.id AND
                signupbox_fieldvalue.field_id = signupbox_field.id AND
                signupbox_field.type = '%s' ORDER BY signupbox_field.id FETCH FIRST 1 ROW ONLY
                """ % TEXT_FIELD,
                'email':
                """
                SELECT value from signupbox_fieldvalue, signupbox_field WHERE
                signupbox_fieldvalue.attendee_id = signupbox_attendee.id AND
                signupbox_fieldvalue.field_id = signupbox_field.id AND
                signupbox_field.type = '%s'
                """ % EMAIL_FIELD,
                'phone':
                """
                SELECT value from signupbox_fieldvalue, signupbox_field WHERE
                signupbox_fieldvalue.attendee_id = signupbox_attendee.id AND
                signupbox_fieldvalue.field_id = signupbox_field.id AND
                signupbox_field.type = '%s'
                """ % PHONE_FIELD
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
    status = models.CharField(max_length=32,
        choices=ATTENDEE_STATUS_CHOICES, default=ATTENDEE_CONFIRMED)
    fields = models.ManyToManyField(Field, through="FieldValue")
    attendee_count = models.PositiveIntegerField(default=1)
    reminder_sent = models.DateTimeField(blank=True, null=True)

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
            except IndexError:
                return ''

    class Meta:
        ordering = ('id',)

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


def create_default_fields(event):
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
    for index, field in enumerate(default_fields):
        Field.objects.create(event=event, **field)

def create_default_tickets(event):
    default_tickets = (
        {'name':ugettext('Default ticket'),},
    )
    for index, ticket in enumerate(default_tickets):
        Ticket.objects.create(event=event, **ticket)

def on_paypal_payment_success(sender, **kwargs):
    ipn_obj = sender
    booking = Booking.objects.get(ordernumber=ipn_obj.item_number)
    booking_confirmed.send(sender=ipn_obj, booking_id=booking.pk)
payment_was_successful.connect(on_paypal_payment_success)

def on_quickpay_payment_success(sender, ordernumber, **kwargs):
    booking = Booking.objects.get(ordernumber=ordernumber.lstrip('0'))
    booking_confirmed.send(sender=sender, booking_id=booking.id, cardtype=sender.cardtype)
quickpay_payment_was_successfull.connect(on_quickpay_payment_success)
