# -*- coding: utf-8 -*-
from dashboard import index, signup
from event import create as event_create, read as event_detail, edit as event_edit
from attendees import event_attendees, event_attendees_edit, event_booking_detail
from tickets import event_tickets, event_tickets_edit, event_tickets_add
from fields import event_fields
from public import event_site, event_register, event_confirm, event_complete, event_incomplete, quickpay_callback
from account import account_settings, account_profile, account_members, account_permissions
__all__ = [
    "index",
    "signup",
    "event_create",
    "event_detail",
    "event_edit",
    "event_attendees",
    "event_attendees_edit",
    "event_booking_detail",
    "event_tickets",
    "event_tickets_edit",
    "event_tickets_add",
    "event_fields",
    "event_site",
    "event_register",
    "event_confirm",
    "event_complete",
    "event_incomplete",
    "account_settings",
    "account_profile",
    "account_members",
    "account_permissions",
    "quickpay_callback",
]
