from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from pucas.ldap import LDAPSearch, LDAPSearchException


class Command(BaseCommand):
    help = 'Look up one or more users in LDAP by netid'

    def add_arguments(self, parser):
        parser.add_argument('netid', nargs='+')

    def handle(self, *args, **options):
        ldap_search = LDAPSearch()
        for netid in options['netid']:
            print('\nLooking for %s...' % netid)
            try:
                info = ldap_search.find_user(netid)
                # display attributes configured in settings
                for attr in settings.PUCAS_LDAP['ATTRIBUTES']:
                    print('%-15s %s' % (attr, getattr(info, attr)))
            except LDAPSearchException as err:
                print(err)

