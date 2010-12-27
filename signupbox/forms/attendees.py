from django import forms
from django.utils.translation import ungettext, ugettext, ugettext_lazy as _

ACTION_CHOICES = (
    ('', _('Actions...')),
    ('confirm', _('Confirm')),
    ('cancel', _('Cancel')),
    ('email', _('Send email')),
    ('export', _('Export')),
)

CSV_EXPORT = 0
PDF_EXPORT = 1
XLS_EXPORT = 2

FORMAT_CHOICES = (
    (CSV_EXPORT, _('Spreadsheet')),
    (PDF_EXPORT, _('PDF')),
    (XLS_EXPORT, _('Excel')),
)

REGISTRATION_DATA = 0
BOOKING_DATA = 1

DATA_CHOICES = (
    (REGISTRATION_DATA, _('Attendee data')),
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

def attendeeactionsform_factory(attendee_qs):
    class AttendeeActionsForm(forms.Form):
        action = forms.CharField(widget=forms.HiddenInput)
        attendees = forms.ModelMultipleChoiceField(
            queryset=attendee_qs,
        )
    return AttendeeActionsForm