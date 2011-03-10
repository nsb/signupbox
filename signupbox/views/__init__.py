# -*- coding: utf-8 -*-
from dashboard import frontpage, index, signup, event_gviz
from event import create as event_create, read as event_detail, edit as event_edit
from attendees import event_attendees, event_attendees_edit, event_booking_detail
from tickets import event_tickets, event_tickets_edit, event_tickets_add
from fields import event_fields
from public import event_site, event_register, event_confirm, event_complete, event_incomplete, event_terms, quickpay_callback
from account import account_settings, account_profile, account_members, account_members_add, account_permissions, account_members_delete, account_invitation, account_invitation_cancel
__all__ = [
    "frontpage",
    "index",
    "signup",
    "event_gviz",
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
    "event_terms",
    "account_settings",
    "account_profile",
    "account_members",
    "account_members_add",
    "account_members_delete",
    "account_permissions",
    "account_invitation",
    "account_invitation_cancel",
    "quickpay_callback",
]
