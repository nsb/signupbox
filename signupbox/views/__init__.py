# -*- coding: utf-8 -*-
from dashboard import frontpage, accounts, index, archived, signup, event_gviz
from event import create as event_create, read as event_detail, edit as event_edit, copy as event_copy, subscribe as event_subscribe, unsubscribe as event_unsubscribe, archive as event_archive, unarchive as event_unarchive
from attendees import event_attendees, event_attendees_edit, event_attendees_add, event_booking_detail
from tickets import event_tickets, event_tickets_edit, event_tickets_add
from fields import event_fields
from public import event_site, event_register, event_confirm, event_complete, event_incomplete, event_view_more, event_terms, quickpay_callback
from account import account_settings, account_profile, account_members, account_members_add, account_permissions, account_members_delete, account_invitation, account_invitation_cancel, account_exports
__all__ = [
    "frontpage",
    "accounts",
    "index",
    "archived",
    "signup",
    "event_gviz",
    "event_create",
    "event_detail",
    "event_edit",
    "event_copy",
    "event_subscribe",
    "event_unsubscribe",
    "event_archive",
    "event_unarchive",
    "event_attendees",
    "event_attendees_edit",
    "event_attendees_add",
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
    "event_view_more",
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
