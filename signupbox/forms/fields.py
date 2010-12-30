from django import forms
from django.forms.models import modelformset_factory

from ..models import Field

class FieldsForm(forms.ModelForm):
    ordering = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Field
        fields = ('label', 'type', 'required', 'in_extra', 'ordering',)

FieldFormset = modelformset_factory(Field, FieldsForm, extra=0, can_delete=True)
