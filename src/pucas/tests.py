from io import StringIO
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.sites import AdminSite
from django.core.management import call_command
from django.test import TestCase, RequestFactory, override_settings
from ldap3.core.exceptions import LDAPCursorError, LDAPException
import pytest

from pucas.admin import CasUserAdmin
from pucas.forms import CasUserInitForm
from pucas.ldap import LDAPSearch, LDAPSearchException, \
    init_cas_user, user_info_from_ldap
from pucas.management.commands import createcasuser, ldapsearch
from pucas.signals import cas_login


class MockLDAPInfo(object):
    '''Simulate ldap result object with ldap3 specific behavior for getattr'''
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, attr):
        # __getattr__ only gets called when the default attribute access
        # falls through, so in this case, we always want that to raise the
        # cursor error
        raise LDAPCursorError


class TestMockLDAPInfo(TestCase):

    def test_init(self):
        mock_info = MockLDAPInfo(a=1, b=2)
        assert mock_info.a == 1
        assert mock_info.b == 2

    def test_getattr(self):
        mock_info = MockLDAPInfo(a=1, b=2)
        with pytest.raises(LDAPCursorError):
            foo = mock_info.c


class TestSignals(TestCase):
    # NOTE: using django TestCase for compatibility with
    # django test runner

    @mock.patch('pucas.signals.user_info_from_ldap')
    def test_cas_login(self, mock_userinit):
        mockuser = mock.Mock()
        # if create is not true, user init method should be called
        cas_login(mock.Mock(), mockuser, False)
        mock_userinit.assert_not_called()

        # if create is true, user init method should be called
        cas_login(mock.Mock(), mockuser, True)
        mock_userinit.assert_called_with(mockuser)


class TestLDAPSearch(TestCase):

    ldap_servers = ['lds81', 'ldap42', 'ld4all']
    dn = 'uid=foo,o= bar org,c=us'
    password = 'baz'

    @mock.patch('pucas.ldap.ldap3')
    @override_settings(PUCAS_LDAP={'SERVERS': ldap_servers})
    def test_init(self, mockldap3):
        # initialize and then check expected behavior against
        # mock ldap3
        LDAPSearch()

        test_servers = []
        for test_server in self.ldap_servers:
            mockldap3.Server.assert_any_call(test_server,
                get_info=mockldap3.ALL, use_ssl=True)

        # initialized servers are collected into server pool
        servers = [mockldap3.Server.return_value
                   for test_server in self.ldap_servers]
        mockldap3.ServerPool.assert_called_with(servers,
            mockldap3.ROUND_ROBIN, active=True, exhaust=5)

        # server pool is used for connection
        mockldap3.Connection.assert_called_with(mockldap3.ServerPool.return_value,
            auto_bind=True)

        with override_settings(PUCAS_LDAP={
            'SERVERS': self.ldap_servers,
            'BIND_DN': self.dn,
            'BIND_PASSWORD': self.password,
         }):
            LDAPSearch()
            # server pool is used for connection, now with password
            mockldap3.Connection.assert_called_with(mockldap3.ServerPool.return_value,
                auto_bind=True, user=self.dn, password=self.password)

        with pytest.raises(LDAPException):
            mockldap3.Connection.side_effect = LDAPException
            LDAPSearch()


    @mock.patch('pucas.ldap.ldap3')
    @override_settings(PUCAS_LDAP={'SERVERS': ldap_servers,
        'ATTRIBUTES': ['uid', 'sn', 'ou'],
        'SEARCH_BASE': 'o=my_org', 'SEARCH_FILTER': "(uid=%(user)s)"})
    def test_find_user(self, mockldap3):
        ldsearch = LDAPSearch()

        # empty netid should error
        with pytest.raises(LDAPSearchException):
            ldsearch.find_user(None)
        with pytest.raises(LDAPSearchException):
            ldsearch.find_user('')

        netid = 'jschmoe'
        # simulate no results
        ldsearch.conn.entries = []

        with pytest.raises(LDAPSearchException) as search_err:
            ldsearch.find_user(netid)
        assert 'No match found for %s' % netid in str(search_err.value)
        # search should use configured values
        ldsearch.conn.search.assert_called_with(settings.PUCAS_LDAP['SEARCH_BASE'],
            settings.PUCAS_LDAP['SEARCH_FILTER'] % {'user': netid},
            attributes=settings.PUCAS_LDAP['ATTRIBUTES'])

        # simulate too many matches
        ldsearch.conn.entries = [mock.Mock(), mock.Mock()]
        with pytest.raises(LDAPSearchException) as search_err:
            ldsearch.find_user(netid)

        assert 'Found more than one entry for %s' % netid in \
            str(search_err.value)

        # simulate one match
        userinfo = mock.Mock()
        ldsearch.conn.entries = [userinfo]
        assert ldsearch.find_user(netid) == userinfo

        # search for all attributes
        ldsearch.find_user(netid, all_attributes=True)
        # should use '*' instead of configured attributes
        ldsearch.conn.search.assert_called_with(settings.PUCAS_LDAP['SEARCH_BASE'],
            settings.PUCAS_LDAP['SEARCH_FILTER'] % {'user': netid},
            attributes='*')

        # with missing configs in any combination
        bad_settings = [
            # nothing set
            {},
            # attributes only
            {'ATTRIBUTES': ['foo']},
            # search filter missing
            {'ATTRIBUTES': ['foo'], 'SEARCH_BASE': 'u=foo'},
            # search base missing
            {'ATTRIBUTES': ['foo'], 'SEARCH_FILTER': '(uid=u)'},
        ]

        for bad_cfg in bad_settings:

            with override_settings(PUCAS_LDAP=bad_cfg):
                with pytest.raises(LDAPSearchException) as search_err:
                    ldsearch.find_user(netid)
            assert 'LDAP is not configured for user lookup' in str(search_err.value)


def extra_user_init(user, user_info):
    user.extra = 'custom init'


@mock.patch('pucas.ldap.LDAPSearch')
class TestUserInfo(TestCase):

    test_attr_map = {'first_name': 'givenName', 'last_name': 'surname',
                     'email': ['mail', 'eduPerson']}

    @override_settings(PUCAS_LDAP={})
    def test_no_attrs(self, mock_ldapsearch):
        mockuser = mock.Mock()

        user_info_from_ldap(mockuser)
        mock_ldapsearch.assert_not_called()

    @override_settings(PUCAS_LDAP={'ATTRIBUTE_MAP': test_attr_map})
    def test_attrs(self, mock_ldapsearch):
        mockuser = mock.Mock(username='jdoe')
        # simulate no user info returned
        mock_ldapsearch.return_value.find_user.return_value = None
        user_info_from_ldap(mockuser)
        # ldap search init should be called with no args
        mock_ldapsearch.assert_called_with()
        # find user should be called with username
        mock_ldapsearch.return_value.find_user.assert_called_with('jdoe')
        # user save should not be called - no data
        mockuser.save.assert_not_called()

        mock_ldapinfo = MockLDAPInfo(
                        eduPerson='jdoe2@example.com',
                        givenName='John',
                        surname='Doe',
                        mail='jdoe@example.com',
                        extra='foo'
                    )
        # first test that list style attributes are set in order, and string
        # attributes are set as given
        mock_ldapsearch.return_value.find_user.return_value = mock_ldapinfo
        user_info_from_ldap(mockuser)
        assert mockuser.first_name == mock_ldapinfo.givenName
        assert mockuser.last_name == mock_ldapinfo.surname
        assert mockuser.email == mock_ldapinfo.mail
        mockuser.save.assert_called_with()

        # second test that should pass over an unset eduPerson attr and
        # set using givenName in list
        # NOTE: recreating mock to clear all assigned attrs
        delattr(mock_ldapinfo, 'mail')
        user_info_from_ldap(mockuser)
        assert mockuser.first_name == mock_ldapinfo.givenName
        assert mockuser.last_name == mock_ldapinfo.surname
        assert mockuser.email == mock_ldapinfo.eduPerson
        mockuser.save.assert_called_with()

        # missing attribute altogether should result in an empty string
        delattr(mock_ldapinfo, 'givenName')
        delattr(mock_ldapinfo, 'surname')
        mockuser = mock.Mock(username='jdoe')
        # set to none to avoid Mock returning a mock and default behavior of
        # getattr
        mockuser.first_name = None
        mockuser.last_name = None
        mock_ldapsearch.return_value.find_user.return_value = mock_ldapinfo
        user_info_from_ldap(mockuser)
        assert mockuser.first_name == ''
        assert mockuser.last_name == ''
        assert mockuser.email == mock_ldapinfo.eduPerson
        mockuser.save.assert_called_with()

    @override_settings(PUCAS_LDAP={'ATTRIBUTE_MAP': test_attr_map,
        'EXTRA_USER_INIT': 'pucas.tests.extra_user_init'})
    def test_extra_init(self, mock_ldapsearch):
        mockuser = mock.Mock(username='jdoe')

        mock_ldapsearch.return_value.find_user.return_value = mock.Mock()
        user_info_from_ldap(mockuser)
        # check for custom field set by test extra init method
        assert mockuser.extra == 'custom init'
        mockuser.save.assert_called_with()


@mock.patch('pucas.management.commands.ldapsearch.LDAPSearch')
@override_settings(PUCAS_LDAP={'ATTRIBUTES': ['foo', 'bar', 'baz']})
class TestLDAPSearchCommand(TestCase):

    def setUp(self):
        self.cmd = ldapsearch.Command()
        # replace stdout/stderr with buffers to inspect output
        self.cmd.stdout = StringIO()
        self.cmd.stderr = StringIO()

    def test_search(self, mock_ldapsearch):
        mock_ldapinfo = mock.Mock(foo='phooey', bar='none', baz='1')
        mock_ldapsearch.return_value.find_user.return_value = mock_ldapinfo
        self.cmd.handle(netid=['jdoe'], all=False)
        mock_ldapsearch.assert_called_with()
        mock_ldapsearch.return_value.find_user.assert_called_with('jdoe',
            all_attributes=False)
        output = self.cmd.stdout.getvalue()
        assert 'Looking for jdoe...' in output
        assert '%-15s %s' % ('foo', 'phooey') in output
        assert '%-15s %s' % ('bar', 'none') in output
        assert '%-15s %s' % ('baz', '1') in output

    def test_search_all_attr(self, mock_ldapsearch):
        mock_ldapsearch.return_value.find_user.return_value = 'full return'
        self.cmd.handle(netid=['jdoe'], all=True)
        mock_ldapsearch.return_value.find_user.assert_called_with('jdoe',
            all_attributes=True)
        output = self.cmd.stdout.getvalue()
        # currently all attributes just prints the returned object
        assert 'full return' in output

    def test_err(self, mock_ldapsearch):
        error_message = 'Error looking for jdoe'
        mock_ldapsearch.return_value.find_user.side_effect = \
            LDAPSearchException(error_message)
        self.cmd.handle(netid=['jdoe'], all=False)
        output = self.cmd.stderr.getvalue()
        assert error_message in output

    def test_call_command(self, mock_ldapsearch):
        call_command('ldapsearch', 'jdoe')
        mock_ldapsearch.return_value.find_user.assert_called_with('jdoe',
            all_attributes=False)


@mock.patch('pucas.management.commands.createcasuser.init_cas_user')
class TestCreateCasUserCommand(TestCase):

    def setUp(self):
        self.cmd = createcasuser.Command()
        self.cmd.stdout = StringIO()
        self.cmd.stderr = StringIO()

    def test_handle(self, mock_init_cas_user):
        mockuser = mock.Mock(is_staff=False, is_superuser=False)
        mock_init_cas_user.return_value = (mockuser, False)
        self.cmd.handle(netids=['jdoe'], admin=False, staff=False)
        mock_init_cas_user.assert_called_with('jdoe')
        # not given staff or superuser permissions
        assert not mockuser.is_staff
        assert not mockuser.is_superuser
        output = self.cmd.stdout.getvalue()
        assert "Updated user 'jdoe'" in output

        # init with staff=True
        self.cmd.handle(netids=['jdoe'], admin=False, staff=True)
        assert mockuser.is_staff
        assert mockuser.is_active
        # init with admin=True
        self.cmd.handle(netids=['jdoe'], admin=True, staff=True)
        assert mockuser.is_staff
        assert mockuser.is_admin
        assert mockuser.is_active

        # created vs updated
        mock_init_cas_user.return_value = (mockuser, True)
        self.cmd.handle(netids=['jschmoe'], admin=True, staff=True)
        output = self.cmd.stdout.getvalue()
        assert "Created user 'jschmoe'" in output

    def test_err(self, mock_init_cas_user):
        mock_init_cas_user.side_effect = LDAPSearchException
        self.cmd.handle(netids=['jdoe'], admin=False, staff=False)
        output = self.cmd.stderr.getvalue()
        assert "LDAP information for 'jdoe' not found" in output

    def test_call_command(self, mock_init_cas_user):
        mock_init_cas_user.side_effect = LDAPSearchException
        call_command('createcasuser', 'jdoe', '--staff')
        mock_init_cas_user.assert_called_with('jdoe')


@mock.patch('pucas.ldap.LDAPSearch')
@mock.patch('pucas.ldap.user_info_from_ldap')
@mock.patch('pucas.ldap.get_user_model')
class TestInitCasUser(TestCase):

    def test_creates_new_user(self, mock_getuser, mock_userinfo, mock_ldapsearch):
        mockuser = mock.Mock()
        mock_getuser.return_value.objects.get_or_create.return_value = (mockuser, True)

        user, created = init_cas_user('jdoe')

        mock_ldapsearch.return_value.find_user.assert_called_with('jdoe')
        mock_getuser.return_value.objects.get_or_create.assert_called_with(username='jdoe')
        # user info should be populated for new users
        mock_userinfo.assert_called_with(mockuser)
        assert user == mockuser
        assert created is True

    def test_existing_user_is_reinitialised(self, mock_getuser, mock_userinfo, mock_ldapsearch):
        mockuser = mock.Mock()
        mock_getuser.return_value.objects.get_or_create.return_value = (mockuser, False)

        user, created = init_cas_user('jdoe')

        # user info should be repopulated for existing users too
        mock_userinfo.assert_called_with(mockuser)
        assert user == mockuser
        assert created is False

    def test_ldap_not_found(self, mock_getuser, mock_userinfo, mock_ldapsearch):
        mock_ldapsearch.return_value.find_user.side_effect = LDAPSearchException

        with pytest.raises(LDAPSearchException):
            init_cas_user('unknown')

        # user record should not be created if LDAP lookup fails
        mock_getuser.return_value.objects.get_or_create.assert_not_called()


class TestCasUserInitForm(TestCase):

    def test_valid_single_netid(self):
        form = CasUserInitForm(data={"netids": "jdoe"})
        assert form.is_valid()
        assert form.cleaned_data["netids"] == ["jdoe"]

    def test_valid_multiple_netids_spaces(self):
        form = CasUserInitForm(data={"netids": "jdoe jschmoe abc123"})
        assert form.is_valid()
        assert form.cleaned_data["netids"] == ["jdoe", "jschmoe", "abc123"]

    def test_valid_multiple_netids_newlines(self):
        form = CasUserInitForm(data={"netids": "jdoe\njschmoe\nabc123"})
        assert form.is_valid()
        assert form.cleaned_data["netids"] == ["jdoe", "jschmoe", "abc123"]

    def test_invalid_netid_special_chars(self):
        form = CasUserInitForm(data={"netids": "jdoe; rm -rf /"})
        assert not form.is_valid()
        assert "netids" in form.errors

    def test_invalid_netid_hyphen(self):
        form = CasUserInitForm(data={"netids": "j-doe"})
        assert not form.is_valid()

    def test_empty_input(self):
        form = CasUserInitForm(data={"netids": ""})
        assert not form.is_valid()


class TestCasUserAdmin(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = CasUserAdmin(get_user_model(), self.site)
        self.factory = RequestFactory()

    @mock.patch("pucas.admin.init_cas_user")
    def test_get_renders_form(self, mock_init):
        request = self.factory.get("/admin/users/user/cas-init/")
        request.user = mock.Mock(is_active=True, is_staff=True)
        # provide session and _messages for admin context
        request.session = {}
        from django.contrib.messages.storage.fallback import FallbackStorage
        request._messages = FallbackStorage(request)

        response = self.admin.cas_user_init(request)
        assert response.status_code == 200
        assert isinstance(response.context_data["form"], CasUserInitForm)

    @mock.patch("pucas.admin.LDAPSearch")
    @mock.patch("pucas.admin.init_cas_user")
    def test_post_creates_new_user(self, mock_init, mock_ldapsearch):
        mock_user = mock.Mock()
        mock_init.return_value = (mock_user, True)
        request = self.factory.post(
            "/admin/users/user/cas-init/", data={"netids": "jdoe"}
        )
        request.user = mock.Mock(is_active=True, is_staff=True)
        request.session = {}
        from django.contrib.messages.storage.fallback import FallbackStorage
        request._messages = FallbackStorage(request)

        response = self.admin.cas_user_init(request)
        mock_init.assert_called_once_with("jdoe", ldap=mock_ldapsearch.return_value)
        # newly created accounts should be activated by the admin
        assert mock_user.is_active is True
        mock_user.save.assert_called()
        # should redirect back to changelist
        assert response.status_code == 302

    @mock.patch("pucas.admin.LDAPSearch")
    @mock.patch("pucas.admin.init_cas_user")
    def test_post_existing_user(self, mock_init, mock_ldapsearch):
        mock_init.return_value = (mock.Mock(), False)
        request = self.factory.post(
            "/admin/users/user/cas-init/", data={"netids": "jdoe"}
        )
        request.user = mock.Mock(is_active=True, is_staff=True)
        request.session = {}
        from django.contrib.messages.storage.fallback import FallbackStorage
        request._messages = FallbackStorage(request)

        response = self.admin.cas_user_init(request)
        mock_init.assert_called_once_with("jdoe", ldap=mock_ldapsearch.return_value)
        assert response.status_code == 302

    @mock.patch("pucas.admin.LDAPSearch")
    @mock.patch("pucas.admin.init_cas_user")
    def test_post_ldap_not_found(self, mock_init, mock_ldapsearch):
        mock_init.side_effect = LDAPSearchException("not found")
        request = self.factory.post(
            "/admin/users/user/cas-init/", data={"netids": "unknown"}
        )
        request.user = mock.Mock(is_active=True, is_staff=True)
        request.session = {}
        from django.contrib.messages.storage.fallback import FallbackStorage
        request._messages = FallbackStorage(request)

        response = self.admin.cas_user_init(request)
        # still redirects; error shown via message_user
        assert response.status_code == 302

    @mock.patch("pucas.admin.init_cas_user")
    def test_post_invalid_netid_does_not_call_init(self, mock_init):
        request = self.factory.post(
            "/admin/users/user/cas-init/", data={"netids": "j doe!"}
        )
        request.user = mock.Mock(is_active=True, is_staff=True)
        request.session = {}
        from django.contrib.messages.storage.fallback import FallbackStorage
        request._messages = FallbackStorage(request)

        response = self.admin.cas_user_init(request)
        mock_init.assert_not_called()
        # invalid form re-renders, no redirect
        assert response.status_code == 200

    def test_change_list_template(self):
        assert self.admin.change_list_template == "admin/pucas/user_change_list.html"

    def test_get_urls_includes_cas_init(self):
        urls = self.admin.get_urls()
        url_names = [u.name for u in urls if hasattr(u, 'name')]
        assert "users_user_cas_init" in url_names
