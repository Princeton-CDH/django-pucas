from django.core.management.base import BaseCommand

from pucas.ldap import LDAPSearchException, init_cas_user


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
        netids = options['netids']
        admin = options['admin']
        staff = options['staff']
        for netid in netids:
            try:
                user, created = init_cas_user(netid)

                # If admin flag is set, make the user an admin
                if admin or staff:
                    user.is_staff = True
                    if admin:
                        user.is_superuser = True
                    user.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        "%s user '%s'"
                        % ('Created' if created else 'Updated', netid)))

            except LDAPSearchException:
                self.stderr.write(
                    self.style.ERROR("LDAP information for '%s' not found"
                                     % netid))
