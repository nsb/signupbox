from django import forms
from django.utils.translation import ungettext, ugettext, ugettext_lazy as _

ACTION_CHOICES = (
    ('', _('Actions...')),
    ('confirm', _('Confirm')),
    ('cancel', _('Cancel')),
    ('email', _('Send email')),
    ('export', _('Export')),
)


def attendeeactionsform_factory(attendee_qs):
    class AttendeeActionsForm(forms.Form):
        action = forms.CharField(widget=forms.HiddenInput)
        attendees = forms.ModelMultipleChoiceField(
            queryset=attendee_qs,
        )
    return AttendeeActionsForm