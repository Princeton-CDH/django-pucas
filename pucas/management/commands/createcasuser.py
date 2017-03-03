from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from pucas.ldap import LDAPSearch, LDAPSearchException, \
    user_info_from_ldap


class Command(BaseCommand):
    help = 'Initialize a new CAS user account'

    def add_arguments(self, parser):
        parser.add_argument('netids', nargs='+')
        parser.add_argument(
            '--admin',
            help='Give the specified user(s) superuser permissions (equivalent to createsuperuser)',
            action='store_true',
            default=False
        )
        parser.add_argument(
            '--staff',
            help='Give the specified user(s) staff permissions',
            action='store_true',
            default=False
        )

    def handle(self, *args, **options):
        User = get_user_model()

        ldap_search = LDAPSearch()
        netids = options['netids']
        admin = options['admin']
        staff = options['staff']
        for netid in netids:
            try:
                # make sure we can find the netid in LDAP first
                ldap_search.find_user(netid)
                user, created = User.objects.get_or_create(username=netid)
                # NOTE: should we re-init data from ldap even if user
                # already exists, or error?
                user_info_from_ldap(user)

                # If admin flag is set, make the user an admin
                if admin or staff:
                    user.is_staff = True
                    if admin:
                        user.is_superuser = True
                    user.save()

                self.stdout.write(
                    self.style_success("%s user '%s'"  \
                        % ('Created' if created else 'Updated', netid)))

            except LDAPSearchException:
                self.stderr.write(
                    self.style.ERROR("LDAP information for '%s' not found"  \
                        % netid))

    def style_success(self, msg):
        # workaround to support django 1.8 - style.SUCCESS
        # only added in django 1.9
        if hasattr(self.style, 'SUCCESS'):
            return self.style.SUCCESS(msg)
        else:
            return msg

