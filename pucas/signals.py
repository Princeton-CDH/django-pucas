from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver

from django_cas_ng.signals import cas_user_authenticated

from pucas.ldapsearch import LDAPSearch


@receiver(cas_user_authenticated)
def cas_login(sender, user, created, attributes, ticket, service, **kwargs):
    # Do an LDAP lookup to populate user data. Since CAS authentication
    # succeeded, should be no ambiguity in finding user info.

    # configured mapping of user fields to ldap fields
    attr_map = settings.PUCAS_LDAP['ATTRIBUTE_MAP']

    # only populate attributes when a new user is created
    if created:
        user_info = LDAPSearch().find_user(user.username)
        if user_info:
            for user_attr, ldap_attr in attr_map.items():
                if isinstance(ldap_attr, dict):
                    rel_model = getattr(user, user_attr)
                    for rel_attr, rel_ldap_attr in ldap_attr.items():
                        setattr(rel_model, rel_attr,
                            getattr(user_info, rel_ldap_attr))

                else:
                    setattr(user, user_attr, getattr(user_info, ldap_attr))

            user.save()
