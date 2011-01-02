from django import forms
from django.forms.models import modelformset_factory

from ..models import Field, FieldOption

def fieldformset_factory(event):

    class FieldsForm(forms.ModelForm):
        ordering = forms.IntegerField(required=False, widget=forms.HiddenInput)

        def save(self, *args, **kwargs):
            self.instance.event = event
            super(FieldsForm, self).save(*args, **kwargs)
            self.instance.options.all().delete()
            for value in self.data.getlist('%s-options' % self.prefix):
                if value:
                    FieldOption.objects.create(field=self.instance, value=value)
            return self.instance

        def has_changed(self):
            return True

        class Meta:
            model = Field
            fields = ('label', 'type', 'required', 'in_extra', 'ordering',)

    FieldFormset = modelformset_factory(Field, FieldsForm, extra=0, can_delete=True)
    return FieldFormset
