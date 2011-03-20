from datetime import datetime, time

from django import forms
from django.forms.fields import MultiValueField, EMPTY_VALUES
from django.forms.widgets import MultiWidget, Input
from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _

class DateInput(forms.DateInput):
    #input_type = 'date'
    pass

class SearchInput(Input):
    input_type = 'search'

class AccountWidget(forms.TextInput):
    """
    Append .domain name to input field

    """
    def render(self, name, value, attrs=None):
        return mark_safe(
            ''.join((
                super(AccountWidget, self).render(name, value, attrs),
                '<strong class="large">.%s</strong>' % Site.objects.get_current().domain,
            ))
        )


HOUR_CHOICES = (
    ('0','00'),
    ('1','01'),
    ('2','02'),
    ('3','03'),
    ('4','04'),
    ('5','05'),
    ('6','06'),
    ('7','07'),
    ('8','08'),
    ('9','09'),
    ('10','10'),
    ('11','11'),
    ('12','12'),
    ('13','13'),
    ('14','14'),
    ('15','15'),
    ('16','16'),
    ('17','17'),
    ('18','18'),
    ('19','19'),
    ('20','20'),
    ('21','21'),
    ('22','22'),
    ('23','23')
)
 
MINUTE_CHOICES = (
    ('00','00'),
    ('15','15'),
    ('30','30'),
    ('45','45')
)
 
class TimeSelectWidget(MultiWidget):
    """
    Time Widget, see TimeSelectField for info.
    """
    def __init__(self, *args, **kwargs):
        widgets = (
            forms.Select(choices=HOUR_CHOICES),
            forms.Select(choices=MINUTE_CHOICES)
        )
        super(TimeSelectWidget, self).__init__(widgets, *args, **kwargs)
 
    def decompress(self, value):
        if value:
            return [str(value.hour), str(value.minute)]
        return [None, None]
 
    def format_output(self, rendered_widgets):
        return u'\n:\n'.join(rendered_widgets)
 
class TimeSelectField(MultiValueField):
    """
    Time multi field. Returns datetime.time object. Must be used together with TimeWidget
    """
    def __init__(self, *args, **kwargs):
        fields = (
            forms.ChoiceField(choices=HOUR_CHOICES),
            forms.ChoiceField(choices=MINUTE_CHOICES)
        )
        super(TimeSelectField, self).__init__(fields, *args, **kwargs)
 
    def compress(self, data_list):
        if data_list:
            return time(hour=int(data_list[0]), minute=int(data_list[1]))
        return None

class DateTimeWidget(MultiWidget):
    """
    DateTime Widget, see DateTimeField for info.
    """
    def __init__(self, *args, **kwargs):
        widgets = (
            DateInput(attrs={'class':'datetime', 'autocomplete':'off'}),
            TimeSelectWidget,
        )
        super(DateTimeWidget, self).__init__(widgets, *args, **kwargs)
 
    def decompress(self, value):
        if value:
            return [value.date(), value.time()]
        return [None, None]
 
    def format_output(self, rendered_widgets):
        return u' %(at)s\n'.join(rendered_widgets) % {'at':ugettext('at')}
 
class DateTimeField(MultiValueField):
    """
    DateTime multi field. Returns datetime.datetime object. Must be used together with DateTimeWidget
    """
    widget = DateTimeWidget
    default_error_messages = {
        'invalid_date': _(u'Enter a valid date.'),
        'invalid_time': _(u'Enter a valid time.'),
    }

    def __init__(self, *args, **kwargs):
        errors = self.default_error_messages.copy()
        if 'error_messages' in kwargs:
            errors.update(kwargs['error_messages'])
        fields = (
            forms.DateField(),
            TimeSelectField(),
        )
        super(DateTimeField, self).__init__(fields, *args, **kwargs)
 
    def compress(self, data_list):
        if data_list:
            # Raise a validation error if time or date is empty
            # (possible if DateTimeField has required=False).
            if data_list[0] in EMPTY_VALUES:
                raise forms.ValidationError(self.error_messages['invalid_date'])
            if data_list[1] in EMPTY_VALUES:
                raise forms.ValidationError(self.error_messages['invalid_time'])
            return datetime.combine(data_list[0], data_list[1])
        return None
