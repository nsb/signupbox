from django import forms

from ..models import Ticket

class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = ('name', 'offered_from', 'offered_to', 'price', 'currency',)
