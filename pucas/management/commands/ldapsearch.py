from django.conf import settings
from django.core.management.base import BaseCommand

from pucas.ldap import LDAPSearch, LDAPSearchException


class Command(BaseCommand):
    help = 'Look up one or more users in LDAP by netid'

    def add_arguments(self, parser):
        parser.add_argument('netid', nargs='+')
        parser.add_argument('--all', '-a', action='store_true',
            help='Retrieve all available LDAP attributes')

    def handle(self, *args, **options):
        ldap_search = LDAPSearch()
        print(options['all'])
        for netid in options['netid']:
            print('\nLooking for %s...' % netid)
            try:
                info = ldap_search.find_user(netid, all_attributes=options['all'])
                # if all attributes were requested, just print the returned
                # ldap search object
                if options['all']:
                    print(info)
                # otherwise, display attributes configured in settings
                else:
                    for attr in settings.PUCAS_LDAP['ATTRIBUTES']:
                        print('%-15s %s' % (attr, getattr(info, attr)))
            except LDAPSearchException as err:
                print(err)

