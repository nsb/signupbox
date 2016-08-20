from django import forms
from django.utils.functional import curry
from django.forms.formsets import BaseFormSet, formset_factory
from django.utils.translation import ugettext, ungettext, ugettext_lazy as _

from ..constants import *
from ..models import Field, FieldValue, Ticket, Booking, Attendee
from ..signals import booking_confirmed

FIELD_TYPES = {
    TEXT_FIELD: curry(forms.CharField,
                      widget=forms.TextInput(attrs={'class': 'form-control'})),
    TEXTAREA_FIELD: curry(forms.CharField,
                          widget=forms.Textarea(attrs={'class': 'form-control'})),
    CHECKBOX_FIELD: curry(forms.BooleanField,
                          widget=forms.CheckboxInput(attrs={'class': 'form-control'})),
    EMAIL_FIELD: curry(forms.EmailField,
                       widget=forms.TextInput(attrs={'class': 'form-control'})),
    SELECT_FIELD: curry(forms.ChoiceField,
                        widget=forms.Select(attrs={'class': 'form-control'})),
    RADIOBUTTON_FIELD: curry(forms.ChoiceField,
                             widget=forms.RadioSelect()),
    PHONE_FIELD: curry(forms.CharField,
                       widget=forms.TextInput(attrs={'class': 'form-control'})),
}

def attendeeform_factory(event, is_extra, instance=None):
    """
    creates a form from fields list
    """

    fields_qs = event.fields.all()
    ticket_qs = event.tickets_available.all()

    if is_extra:
        fields_qs = fields_qs.filter(in_extra=True)

    def _save(self, booking=None):

        fields = dict((field.name, field) for field in fields_qs)

        ticket = self.cleaned_data['ticket'] if event.has_extra_forms and ticket_qs.count() > 1 else ticket_qs.all()[0]

        attendee = instance or Attendee.objects.create(booking=booking, ticket=ticket)

        if instance:
            attendee.ticket = ticket

        attendee.attendee_count = self.cleaned_data.get('attendee_count', attendee.attendee_count)
        attendee.save()

        for field in fields:
            fv, created = FieldValue.objects.get_or_create(attendee=attendee, field=fields[field])
            fv.value = self.cleaned_data[field]
            fv.save()

        return attendee

    fields = {'save': _save}

    for field in fields_qs:

        field_args = []

        field_kwargs = {
            'label':field.label,
            'help_text':field.help_text,
            'required':field.required,
        }

        if field.type in (SELECT_FIELD, RADIOBUTTON_FIELD):
            choices = ((choice.value, choice.value) for choice in field.options.all())
            field_kwargs.update({'choices':choices})

        fields[field.name] = FIELD_TYPES[field.type](*field_args, **field_kwargs)

    if event.has_extra_forms and ticket_qs.count() > 1:
        fields['ticket'] = forms.ModelChoiceField(queryset=ticket_qs, empty_label=None, label=_('Ticket'))

    if not event.has_extra_forms:

        max_available = min(event.capacity - event.confirmed_attendees_count + 1 + (
            instance.attendee_count if instance else 0), 51) if event.capacity else 51

        fields['attendee_count'] = forms.TypedChoiceField(
            choices=[(val, val) for val in range(1, max_available)], label=_('Number of attendees'),
                coerce=lambda x: int(x), initial=instance.attendee_count if instance else 1)

    return type('AttendeeForm', (forms.Form,), fields)

def attendeeformset_factory(event):
    class AttendeeFormSet(BaseFormSet):

        def _construct_form(self, i, **kwargs):
            """
            Instantiates and returns the i-th form instance in a formset.
            """
            defaults = {'auto_id': self.auto_id, 'prefix': self.add_prefix(i)}
            if self.data or self.files:
                defaults['data'] = self.data
                defaults['files'] = self.files
            if self.initial:
                try:
                    defaults['initial'] = self.initial[i]
                except IndexError:
                    pass
            # Allow extra forms to be empty.
            if i > 0 and i >= self.initial_form_count():
                defaults['empty_permitted'] = True
            defaults.update(kwargs)
            # if i > 0 the form is extra
            form = self.form(i)(**defaults)
            self.add_fields(form, i)
            return form

        def clean(self):
            if any(self.errors):
                # Don't bother validating the formset unless each form is valid on its own
                return

            ticket_map = {}
            for form in self.forms:
                try:
                    ticket = form.cleaned_data['ticket']
                    ticket_map[ticket.pk] = ticket_map.get(ticket.pk, 0) + 1
                except KeyError:
                    continue

            for pk in ticket_map:
                ticket = Ticket.objects.get(pk=pk)
                if ticket.available and ticket.available < (ticket.confirmed_attendee_count + ticket_map[pk]):
                    count = ticket.available - ticket.confirmed_attendee_count
                    raise forms.ValidationError(ungettext(
                        'There is only %(available)d %(ticket_name)s left. Please adjust your ticket choices.',
                        'There are only %(available)d %(ticket_name)s left. Please adjust your ticket choices.', count) % {
                        'available': count,
                        'ticket_name': ticket
                    })

        def save(self):
            booking = Booking.objects.create(event=event)
            for form in self.forms:
                if form.is_valid() and form.cleaned_data:
                    form.save(booking)
            booking.amount = sum((attendee.ticket.price * attendee.attendee_count for attendee in booking.attendees.all()))
            booking.save()
            return booking

    return AttendeeFormSet

def registerform_factory(event, extra=1):
    """
    Attendee formset for event
    """

    max_available = min(event.capacity - event.confirmed_attendees_count, 50) if event.capacity else 50

    # late binding of is_extra, provided by formsets _construct_form
    attendee_form = lambda formset_instance, is_extra: attendeeform_factory(event, is_extra)
    return formset_factory(attendee_form, formset=attendeeformset_factory(event), extra=extra, max_num=max_available)

def emptyregisterform_factory(event, is_extra=False):
    """
    Attendee formset for event
    """
    attendee_form = attendeeform_factory(event, is_extra)
    return formset_factory(attendee_form, formset=attendeeformset_factory(event), extra=0)().empty_form

class ConfirmForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ()

    def save(self, *args, **kwargs):
        super(ConfirmForm, self).save(*args, **kwargs)
        booking_confirmed.send(sender=self.instance, booking_id=self.instance.id)
