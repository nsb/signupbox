from django.contrib import admin

from models import Account, AccountInvite, Event

admin.site.register(Account)
admin.site.register(AccountInvite)
admin.site.register(Event)
