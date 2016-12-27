from django.dispatch import receiver
from django_cas_ng.signals import cas_user_authenticated

from pucas.ldap import user_info_from_ldap


@receiver(cas_user_authenticated)
def cas_login(sender, user, created, **kwargs):
    # Do an LDAP lookup to populate user data. Since CAS authentication
    # succeeded, should be no ambiguity in finding user info.

    # only populate attributes when a new user is created
    if created:
        user_info_from_ldap(user)


