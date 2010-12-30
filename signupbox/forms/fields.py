from django import forms
from django.forms.models import modelformset_factory

from ..models import Field

class FieldsForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = ('label', 'type', 'required', 'in_extra',)

FieldFormset = modelformset_factory(Field, FieldsForm, extra=0)
