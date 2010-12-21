from django import forms

from ..models import Event
from widgets import DateTimeField, DateTimeWidget
from django.utils.translation import ugettext, ugettext_lazy as _

class EventForm(forms.ModelForm):
    begins = DateTimeField(widget=DateTimeWidget)
    ends = DateTimeField(widget=DateTimeWidget)

    class Meta:
        model = Event
        fields = (
            'title', 'description', 'venue', 'begins', 'ends', 'capacity',
        )

    def clean(self):
        if self.cleaned_data['begins'] > self.cleaned_data['ends']:
            raise forms.ValidationError(_('Begin date must be before end date'))
        return self.cleaned_data