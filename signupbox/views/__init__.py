# -*- coding: utf-8 -*-
from dashboard import index, signup
from event import create as event_create, read as event_detail, edit as event_edit
from attendees import event_attendees, event_attendees_edit
from public import event_site, event_register, event_confirm, event_complete
__all__ = [
    "index",
    "signup",
    "event_create",
    "event_detail",
    "event_edit",
    "event_attendees",
    "event_attendees_edit",
    "event_site",
    "event_register",
    "event_confirm",
    "event_complete",]
