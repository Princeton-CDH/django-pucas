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
                    attributes='*'
                    # attributes=settings.PUCAS_LDAP['ATTRIBUTES']
            )
            if self.conn.entries:
                if len(self.conn.entries) > 1:
                    raise LDAPSearchException('Found more than one entry for %s' % netid)

                return self.conn.entries[0]

            else:
                raise LDAPSearchException('No match found for %s' % netid)

        else:
            raise LDAPSearchException('Error: requested LDAP lookup on empty netid')




# BASE = settings.BASE
# SERVERLIST = settings.SERVERLIST
# WHO = settings.WHO
# HOW = settings.HOW
# ATTRIBS = settings.ATTRIBS

# def connect_ldap():

#     server_pool_objects = []

#     for server in SERVERLIST:
#         server_pool_objects.append(
#             Server(
#                 server,
#                 get_info=ALL,
#                 use_ssl=True
#             )
#         )

#     server_pool = ServerPool(
#         server_pool_objects,
#         ROUND_ROBIN,
#         active=True,
#         exhaust=5
#     )

#     try:
#         conn = Connection(
#             server_pool,
#             WHO,
#             HOW,
#             auto_bind=True,
#         )
#     except LDAPException:
#         raise HttpResponseServerError

#     return conn


# def search_ldap(netid):
#     if netid is not None:
#         conn = connect_ldap()

#         conn.search(
#                 BASE,
#                 '(uid={})'.format(netid),
#                 attributes=ATTRIBS
#         )

#         if len(conn.entries) > 1:
#             print('Ambiguous NetID--more than one entry')
#             raise HttpResponseServerError

#         else:
#             person_dict = conn.entries[0].__dict__
#             new_dict = {}
#             for attrib in person_dict:
#                 new_dict[attrib] = str(person_dict[attrib])
#             return new_dict


#     else:
#         raise HttpResponseServerError

# if __name__ == "__main__":
#     search = searchLDAP(sys.argv[1])
#     print(search)
