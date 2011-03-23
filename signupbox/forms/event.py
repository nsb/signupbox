from django import forms

from ..models import Event
from widgets import DateTimeField, DateTimeWidget
from django.utils.translation import ugettext, ugettext_lazy as _

class EventForm(forms.ModelForm):
    begins = DateTimeField(required=True, widget=DateTimeWidget, label=_('Begins'))
    ends = DateTimeField(required=True, widget=DateTimeWidget, label=_('Ends'))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'mceEditor'}),
        label=_('Description'), required=False)

    class Meta:
        model = Event
        fields = (
            'title', 'description', 'venue', 'begins', 'ends', 'capacity', 'status', 'currency',
        )

    def clean(self):
        if set(('begins', 'ends')).issubset(self.cleaned_data) and self.cleaned_data['begins'] > self.cleaned_data['ends']:
            raise forms.ValidationError(_('Begin date must be before end date'))
        return self.cleaned_data