import ldap3
import logging
import importlib

from ldap3.core.exceptions import LDAPException, LDAPCursorError
from django.conf import settings


logger = logging.getLogger(__name__)


class LDAPSearchException(LDAPException):
    pass


class LDAPSearch(object):

    def __init__(self):
        # retrieve settings and initialize connection
        ldap_servers = []
        for server in settings.PUCAS_LDAP['SERVERS']:
            ldap_servers.append(ldap3.Server(server, get_info=ldap3.ALL,
                use_ssl=True))
        server_pool = ldap3.ServerPool(ldap_servers,
            ldap3.ROUND_ROBIN, active=True, exhaust=5)

        # Load username (in DN format) and password, if in settings
        bind_dn = settings.PUCAS_LDAP.get('BIND_DN', None)
        bind_password = settings.PUCAS_LDAP.get('BIND_PASSWORD', None)

        extra_args = {}
        # Use DN and password if set. Otherwise, use anononymous bind.
        if bind_dn and bind_password:
            extra_args.update({'user': bind_dn, 'password': bind_password})

        try:
            self.conn = ldap3.Connection(server_pool, auto_bind=True,
                                         **extra_args)
        except LDAPException as err:
            logging.error('Error establishing LDAP connection: %s', err)
            # re-raise to be caught elsewhere
            raise

    def find_user(self, netid, all_attributes=False):
        if netid:
            # check for required settings and error if not available
            required_configs = ['ATTRIBUTES', 'SEARCH_BASE', 'SEARCH_FILTER']
            if any(req not in settings.PUCAS_LDAP for req in required_configs):
                raise LDAPSearchException('LDAP is not configured for user lookup')

            # for testing, to see all available attributes
            if all_attributes:
                search_attributes = '*'
            else:
                search_attributes = settings.PUCAS_LDAP['ATTRIBUTES']

            self.conn.search(settings.PUCAS_LDAP['SEARCH_BASE'],
                    settings.PUCAS_LDAP['SEARCH_FILTER'] % {'user': netid},
                    attributes=search_attributes)
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
    attr_map = settings.PUCAS_LDAP.get('ATTRIBUTE_MAP', None)
    # if no map is configured, nothing to do
    if not attr_map:
        # is logging sufficient here? or should it be an exception
        logging.warning('No attribute map configured; not populating user info'
                        ' from ldap')
        return

    user_info = LDAPSearch().find_user(user.username)
    if user_info:
        for user_attr, ldap_attr in attr_map.items():
            # Handle issues where an attribute may need to be populated by
            # multiple attributes OR where it is missing.

            # if just a string, convert to a list so handling can be uniform,
            # in cases where a field is multivalued.
            if isinstance(ldap_attr, str):
                ldap_attr = [ldap_attr]

            # iterate through the list items and break on the first one to
            # correct set without raising LDAPCursorError
            # This is a simplification for multivalued fields, since
            # typically we're mapping to only one value.
            for val in ldap_attr:
                try:
                    setattr(user, user_attr, str(getattr(user_info, val)))
                    break
                except LDAPCursorError:
                    pass
            # user getattr to check for a still unset value, in which case
            # set it to an empty string, used in situations where
            # a user is being updated -- and ot make sure values are
            # strings, not lists
            if not getattr(user, user_attr, None):
                setattr(user, user_attr, '')

        # optional custom user-init method set in django config
        extra_init = settings.PUCAS_LDAP.get('EXTRA_USER_INIT', None)
        if extra_init:
            # use importlib to import the module and get hte function
            mod_name, func_name = extra_init.rsplit('.', 1)
            mod = importlib.import_module(mod_name)
            extra_init_func = getattr(mod, func_name)
            extra_init_func(user, user_info)

        user.save()
