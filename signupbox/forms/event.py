from django import forms

from ..models import Event
from widgets import DateTimeField, DateTimeWidget

class EventForm(forms.ModelForm):
    begins = DateTimeField(widget=DateTimeWidget)
    ends = DateTimeField(widget=DateTimeWidget)

    class Meta:
        model = Event
        fields = (
            'title', 'description', 'venue', 'begins', 'ends', 'capacity',
        )