from django.contrib import admin

from models import Account, AccountInvite, Event, Booking, Attendee

admin.site.register(Account)
admin.site.register(AccountInvite)
admin.site.register(Event)
admin.site.register(Booking)
admin.site.register(Attendee)