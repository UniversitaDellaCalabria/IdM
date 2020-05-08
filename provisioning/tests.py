import random
import string
import time

from bs4 import BeautifulSoup as bs

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from identity.models import Identity, AdditionalAffiliation
from ldap_peoples.models import LdapAcademiaUser

from .custom_messages import *
from .models import *
from .utils import get_date_from_string


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


_MAX_HTML_PAGE_LEN = 6038

_uid = 'unittest_john1298731289371283123-kgkgk-{}'.format(randomString())
_passwd = 'Ssmith_67!'
matricola_studente =  '111190{}'.format(randomString())
matricola_dipendente = '982388{}'.format(randomString())
additional_affiliations = [('otherinst.net', 'student', matricola_studente),
                           ('othst.gov', 'employee', matricola_dipendente),]
_test_guy = {'fiscal_code': 'psopql86e56d086s{}'.format(randomString()),
             'surname': 'posto',
             'name': 'pasqualino',
             'email': '{}@yahoo.it'.format(_uid),
             'date_of_birth': get_date_from_string('16/05/1986'),
             'place_of_birth': 'Cosenza',
             'affiliation': ['member', 'student']}

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
        d = LdapAcademiaUser.objects.filter(uid__contains='unittest_john1298731289371283123-kgkgk')
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
        # check = (b'errorlist' in request.content)
        check = (b'alert-error' in request.content)
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
                                'password_verifica': _passwd+_passwd},
                         follow=True)
        self.assertEqual(request.status_code, 200)
        check = (b'alert-error' in request.content)
        self.assertFalse(check)

    # def test_d_changedata(self):
        """test account change identity data"""
        c = Client()
        lurl = reverse('provisioning:provisioning_login')
        request = c.post(lurl, {'username': _uid,
                                'password': _passwd+_passwd})
        self.assertEqual(request.status_code, 302)

        lurl = reverse('provisioning:change_data')
        request = c.post(lurl, {'mail': 'ingo_'+_test_guy['email'],
                                'telephoneNumber': '0984567683'})
        self.assertEqual(request.status_code, 200)
        #self.assertEqual(request.status_code, 302)
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

    # def test_change_username(self):
        user_model = apps.get_model(settings.AUTH_USER_MODEL)
        django_user = user_model.objects.get(username=_uid)
        self.assertFalse(django_user.change_username)
        c = Client()

        # login
        lurl = reverse('provisioning:provisioning_login')
        request = c.post(lurl, {'username': _uid,
                                'password': _passwd+_passwd})
        self.assertEqual(request.status_code, 302)

        # try to access to change username page (fails!)
        change_username_url = reverse('provisioning:change_username')
        request = c.get(change_username_url, follow=True)
        self.assertEqual(request.status_code, 403)

        # update change_username to True
        django_user.change_username = True
        django_user.save()
        assert django_user.change_username

        # try to access to change username page (success!)
        change_username_url = reverse('provisioning:change_username')
        request = c.get(change_username_url)
        self.assertEqual(request.status_code, 200)

        # create a blacklisted username
        _blacklisted = 'blacklisted'
        ChangedUsername.objects.create(old_username=_blacklisted,
                                       new_username='')

        # choose a blacklisted new username
        lurl = reverse('provisioning:change_username')
        request = c.post(lurl, {'old_username': _uid,
                                'new_username': _blacklisted,
                                'confirm_new_username': _blacklisted},
                         follow=True)
        check = (b'alert-error' in request.content)
        self.assertEqual(request.status_code, 200)
        assert check

        # choose a valid new username
        lurl = reverse('provisioning:change_username')
        _new_uid = '_new__'+ _uid
        request = c.post(lurl, {'old_username': _uid,
                                'new_username': _new_uid,
                                'confirm_new_username': _new_uid},
                         follow=True)
        self.assertEqual(request.status_code, 200)
        # check = (b'errorlist' in request.content)
        check = (b'alert-error' not in request.content)
        assert check

        # check change username token
        d = LdapAcademiaUser.objects.filter(uid=_uid).first()
        p = IdentityLdapChangeConfirmation.objects.filter(ldap_dn=d.dn).last()
        token_url = p.get_activation_url()
        request = c.get(token_url, follow=True)
        self.assertIs(request.status_code, 200)

        # check username and dn consistence
        user = get_user_model().objects.get(username=_new_uid)
        lu = LdapAcademiaUser.objects.get(uid=_new_uid)
        assert _new_uid == user.username
        assert user.dn == lu.dn
        assert _new_uid in lu.eduPersonPrincipalName

        # login
        lurl = reverse('provisioning:provisioning_login')
        request = c.post(lurl, {'username': _new_uid,
                                'password': _passwd+_passwd})
        self.assertEqual(request.status_code, 302)

        # try to access to change username page
        # fails: username can be changed only one time
        change_username_url = reverse('provisioning:change_username')
        request = c.get(change_username_url, follow=True)
        self.assertEqual(request.status_code, 403)

    # def test_d_clean(self):
        # """cleanup"""
        d = LdapAcademiaUser.objects.filter(uid=_new_uid).first()
        print('\nCreated User Attributes:\n')
        for k,v in d.__dict__.items():
            if k[0] == '_': continue
            print('\t{}: {}'.format(k, v))
        if _PURGE_LDAP_TEST_USER:
            d.delete()
