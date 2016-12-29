from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from pucas.ldap import LDAPSearch, LDAPSearchException, \
    user_info_from_ldap


class Command(BaseCommand):
    help = 'Initialize a new CAS user account'

    def add_arguments(self, parser):
        parser.add_argument('netid')

        # TODO: add options to set give new user account superuser/staff
        # permissions

    def handle(self, *args, **options):
        User = get_user_model()

        ldap_search = LDAPSearch()
        netid = options['netid']

        try:
            # make sure we can find the netid in LDAP first
            ldap_search.find_user(netid)
            user, created = User.objects.get_or_create(username=netid)
            # NOTE: should we re-init data from ldap even if user
            # already exists, or error?
            user_info_from_ldap(user)

        except LDAPSearchException:
            self.stderr.write(
                self.style.ERROR("LDAP information for '%s' not found"  \
                    % netid))

