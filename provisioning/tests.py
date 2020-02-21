import time

from bs4 import BeautifulSoup as bs

from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse

from identity.models import Identity, AdditionalAffiliation
from ldap_peoples.models import LdapAcademiaUser

from .custom_messages import *
from .models import *
from .utils import get_date_from_string

_MAX_HTML_PAGE_LEN = 6038

_test_guy = {'fiscal_code': 'psopql86e56d086s',
             'surname': 'posto',
             'name': 'pasqualino',
             'email': 'peppelinux@yahoo.it',
             'date_of_birth': get_date_from_string('16/05/1986'),
             'place_of_birth': 'Cosenza',
             'affiliation': 'student'}

_uid = 'unittest_john1298731289371283123-kgkgk'
_passwd = 'Ssmith_67!'
matricola_studente =  '111190'
matricola_dipendente = '982388'
additional_affiliations = [('otherinst.net', 'student', matricola_studente),
                           ('othst.gov', 'employee', matricola_dipendente),]

_PURGE_LDAP_TEST_USER = True
_WAIT_FOR_A_CHECK = False

class ProvisioningTestCase(TestCase):
    databases = '__all__'

    def setUp(self):
        """test identity creation"""
        # cleanup
        pass

    def test_entire_provisioning(self):
        """test identity account provisioning"""
        d = Identity.objects.filter(**_test_guy)
        for i in d:
            i.delete()

        d = LdapAcademiaUser.objects.filter(uid=_uid).first()
        if d and _PURGE_LDAP_TEST_USER:
            d.delete()

        d = Identity.objects.create(**_test_guy)
        # additional affiliations
        for addaff in additional_affiliations:
            AdditionalAffiliation.objects.create(identity=d,
                                                 origin=addaff[0],
                                                 name=addaff[1],
                                                 unique_code=addaff[2])

        d = Identity.objects.get(email=_test_guy['email'])
        p = IdentityProvisioning.objects.create(identity=d)
        token_url = p.get_activation_url()
        c = Client()
        request = c.post(token_url, {'username': _uid,
                                     'password': _passwd,
                                     'password_verifica': _passwd,
                                     'mail': _test_guy['email']})
        check = (b'errorlist' in request.content)
        if check:
            print(bs(request.content, features="html.parser").prettify()[:_MAX_HTML_PAGE_LEN])
        self.assertIs(check, False)

        # check real user existence
        d = LdapAcademiaUser.objects.filter(uid=_uid).first()
        self.assertTrue(d)
        self.assertTrue(d.userPassword)
        self.assertTrue(d.sambaNTPassword)
        # print(d.userPassword)

    # def test_b_login(self):
        """test account login"""
        c = Client()
        lurl = reverse('provisioning:provisioning_login')
        request = c.post(lurl, {'username': _uid,
                                'password': _passwd})
        # self.assertEqual(int(request.status_code), 302)
        self.assertEqual(request.status_code, 302)

    # def test_c_password_change(self):
        """test a password change with confirmation"""
        c = Client()
        # login first
        lurl = reverse('provisioning:provisioning_login')
        request = c.post(lurl, {'username': _uid,
                                'password': _passwd})

        lurl = reverse('provisioning:change_password')
        request = c.post(lurl, {'old_password': _passwd,
                                'password': _passwd+_passwd,
                                'password_verifica': _passwd+_passwd})
        # self.assertEqual(request.status_code, 200)
        self.assertEqual(request.status_code, 302)

    # def test_d_changedata(self):
        """test account change deliveries data"""
        c = Client()
        lurl = reverse('provisioning:provisioning_login')
        request = c.post(lurl, {'username': _uid,
                                'password': _passwd+_passwd})
        self.assertEqual(request.status_code, 302)

        lurl = reverse('provisioning:change_deliveries')
        request = c.post(lurl, {'mail': 'ingo_'+_test_guy['email'],
                                'telephoneNumber': '0984567683'})
        # self.assertEqual(request.status_code, 200)
        self.assertEqual(request.status_code, 302)
        check = (b'errorlist' in request.content)
        # if check:
            # print(bs(request.content, features="html.parser").prettify()[:_MAX_HTML_PAGE_LEN])
        self.assertIs(check, False)

        # check change token
        d = LdapAcademiaUser.objects.filter(uid=_uid).first()
        p = IdentityLdapChangeConfirmation.objects.filter(ldap_dn=d.dn).last()
        token_url = p.get_activation_url()
        request = c.get(token_url)
        self.assertIs(request.status_code, 200)

        # check forgot your password token
        c = Client()
        lurl = reverse('provisioning:reset_password_ask')
        request = c.post(lurl, {'username': _uid,
                                'mail': 'ingo_'+_test_guy['email']})
        # self.assertEqual(request.status_code, 200)
        self.assertEqual(request.status_code, 302)
        p = IdentityLdapPasswordReset.objects.filter(ldap_dn=d.dn).last()
        token_url = p.get_activation_url()
        request = c.post(token_url, {'username': _uid,
                                     'mail': 'ingo_'+_test_guy['email'],
                                     'password': _passwd+_passwd,
                                     'password_verifica': _passwd+_passwd})
        self.assertIs(request.status_code, 200)
        # print(request.content)

        if _WAIT_FOR_A_CHECK:
            time.sleep(6000)

    # def test_d_clean(self):
        """cleanup"""
        d = LdapAcademiaUser.objects.filter(uid=_uid).first()
        for k,v in d.__dict__.items():
            print('{}: {}'.format(k, v))
        if _PURGE_LDAP_TEST_USER:
            d.delete()

    # def test_change_username_permission(self):

