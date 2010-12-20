from django import forms
from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe

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
