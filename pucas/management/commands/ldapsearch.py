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
        for netid in options['netid']:
            self.stdout.write('\nLooking for %s...' % netid)
            try:
                info = ldap_search.find_user(netid, all_attributes=options['all'])
                # if all attributes were requested, just print the returned
                # ldap search object
                if options['all']:
                    self.stdout.write(info)
                # otherwise, display attributes configured in settings
                else:
                    for attr in settings.PUCAS_LDAP['ATTRIBUTES']:
                        self.stdout.write('%-15s %s' % (attr, getattr(info, attr)))
            except LDAPSearchException as err:
                self.stderr.write(self.style.ERROR(str(err)))

