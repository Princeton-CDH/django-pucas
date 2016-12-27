from unittest import mock
from django.conf import settings
from django.test import TestCase, override_settings
from ldap3.core.exceptions import LDAPException
import pytest

from pucas.ldap import LDAPSearch, LDAPSearchException
from pucas.signals import cas_login


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

        assert 'No match found for %s' % netid in str(search_err)
        # search should use configured values
        ldsearch.conn.search.assert_called_with(settings.PUCAS_LDAP['SEARCH_BASE'],
            settings.PUCAS_LDAP['SEARCH_FILTER'] % {'user': netid},
            attributes=settings.PUCAS_LDAP['ATTRIBUTES'])

        # simulate too many matches
        ldsearch.conn.entries = [mock.Mock(), mock.Mock()]
        with pytest.raises(LDAPSearchException) as search_err:
            ldsearch.find_user(netid)

        assert 'Found more than one entry for %s' % netid in str(search_err)

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
            assert 'LDAP is not configured for user lookup' in str(search_err)




