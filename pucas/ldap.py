import sys
import ldap3
import logging

# from ldap3 import Server, ServerPool, Connection, ALL, ROUND_ROBIN
from ldap3.core.exceptions import LDAPException
from django.conf import settings
from django.http import HttpResponseServerError


logger = logging.getLogger(__name__)

class LDAPSearchException(LDAPException):
    pass


class LDAPSearch(object):

    def __init__(self):
        # retrieve settings and initialize connection
        ldap_servers = []
        for server in settings.PUCAS_LDAP['SERVERS']:
            ldap_servers = ldap3.Server(server, get_info=ldap3.ALL,
                use_ssl=True)
        server_pool = ldap3.ServerPool(ldap_servers,
            ldap3.ROUND_ROBIN, active=True, exhaust=5)

        try:
            self.conn = ldap3.Connection(server_pool, auto_bind=True)
        except LDAPException as err:
            logging.error('Error establishing LDAP connection: %s' % err)
            # re-raise to be caught elsewhere
            raise

    def find_user(self, netid):
        if netid:
            self.conn.search(settings.PUCAS_LDAP['SEARCH_BASE'],
                    settings.PUCAS_LDAP['SEARCH_FILTER'] % {'user': netid},
                    # NOTE: for testing, to see all available attributes,
                    # use wildcard
                    # attributes='*'
                    attributes=settings.PUCAS_LDAP['ATTRIBUTES']
            )
            if self.conn.entries:
                if len(self.conn.entries) > 1:
                    raise LDAPSearchException('Found more than one entry for %s' % netid)

                return self.conn.entries[0]

            else:
                raise LDAPSearchException('No match found for %s' % netid)

        else:
            raise LDAPSearchException('Error: requested LDAP lookup on empty netid')


def user_info_from_ldap(user):
    '''Populate django user info from ldap'''

    # configured mapping of user fields to ldap fields
    attr_map = settings.PUCAS_LDAP['ATTRIBUTE_MAP']

    user_info = LDAPSearch().find_user(user.username)
    if user_info:
        for user_attr, ldap_attr in attr_map.items():
            setattr(user, user_attr, getattr(user_info, ldap_attr))

        user.save()

