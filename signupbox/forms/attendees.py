from django import forms
from django.utils.translation import ungettext, ugettext, ugettext_lazy as _

from ..constants import *

from ..models import Booking

from widgets import SearchInput

ACTION_CHOICES = (
    ('', _('Actions...')),
    ('confirm', _('Confirm')),
    ('cancel', _('Cancel')),
    ('email', _('Send email')),
    ('export', _('Export')),
)

FORMAT_CHOICES = (
    (CSV_EXPORT, _('Spreadsheet')),
    (PDF_EXPORT, _('PDF')),
    (XLS_EXPORT, _('Excel')),
)

DATA_CHOICES = (
    (ATTENDEE_DATA, _('Attendee data')),
    (BOOKING_DATA, _('Booking data')),
)

class AttendeesExportForm(forms.Form):
    format = forms.TypedChoiceField(
        choices=FORMAT_CHOICES,
        label=_('Export as'),
        widget=forms.Select,
        coerce=lambda x: int(x),
    )
    data = forms.TypedChoiceField(
        choices=DATA_CHOICES,
        label=_('Data to export'),
        widget=forms.Select,
        coerce=lambda x: int(x),
    )

class AttendeesEmailForm(forms.Form):
    subject = forms.CharField(label=_('Subject'))
    message = forms.CharField(label=_('Message'), widget=forms.Textarea)
    receive_copy = forms.BooleanField(label=_('Send copy to self?'), initial=False, required=False)

def attendeeactionsform_factory(attendee_qs):
    class AttendeeActionsForm(forms.Form):
        action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.Select(attrs={'disabled':'disabled'}))
        attendees = forms.ModelMultipleChoiceField(
            queryset=attendee_qs,
        )
    return AttendeeActionsForm

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('notes',)

class FilterForm(forms.Form):
    find = forms.CharField(label=_('Search'), required=False, widget=SearchInput)
    show = forms.ChoiceField(
        label=_('Show'),
        choices=(('', _('All')), (ATTENDEE_CONFIRMED, _('Confirmed')), (ATTENDEE_CANCELLED, _('Cancelled'))),
        required=False,
        widget=forms.RadioSelect
    )
