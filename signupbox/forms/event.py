from django import forms

from ..models import Event, RelationWiseSurvey
from widgets import DateTimeField, DateTimeWidget
from django.utils.translation import ugettext, ugettext_lazy as _

class EventForm(forms.ModelForm):
    begins = DateTimeField(required=True, widget=DateTimeWidget, label=_('Begins'))
    ends = DateTimeField(required=True, widget=DateTimeWidget, label=_('Ends'))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'mceEditor'}),
        label=_('Description'), required=False)

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['survey'].queryset = RelationWiseSurvey.objects.filter(account=self.instance.account)

    class Meta:
        model = Event
        fields = (
            'title',
            'description',
            'venue',
            'address',
            'city',
            'zip_code',
            'begins',
            'ends',
            'capacity',
            'status',
            'currency',
            'send_reminder',
            'reminder',
            'language',
            'project_id',
            'survey',
            'show_newsletter_subscribe',
        )

    def clean(self):
        if set(('begins', 'ends')).issubset(self.cleaned_data) and self.cleaned_data['begins'] > self.cleaned_data['ends']:
            raise forms.ValidationError(_('Begin date must be before end date'))
        return self.cleaned_data

class EventCopyForm(forms.Form):
    title = forms.CharField(required=True, label=_('New title'))
