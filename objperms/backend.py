# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType

from objperms.models import ObjectPermission

class ObjectPermBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = False

    def authenticate(self, username, password):
        return None

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_authenticated():
            return False

        if obj is None:
            return False

        try:
            ct = ContentType.objects.get_for_model(obj)
        except AttributeError:
            return False # djangos tests run with a non model obj. Gives us an _meta attribute missing

        try:
            perm = perm.split('.')[-1].split('_')[0]
        except IndexError:
            return False

        p = ObjectPermission.objects.filter(content_type=ct,
                                            object_id=obj.id,
                                            user=user_obj)
        return p.filter(**{'can_%s' % perm: True}).exists()
