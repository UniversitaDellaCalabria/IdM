import random
import string
import time

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from identity.models import Identity, AdditionalAffiliation
from ldap_peoples.models import LdapAcademiaUser

from .custom_messages import *
from .models import *
from .utils import (get_date_from_string,
                    get_available_ldap_usernames)


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


_MAX_HTML_PAGE_LEN = 6038

_uid = 'unit_test_user' #-{}'.format(randomString())
_new_uid = '_new__'+ _uid
_passwd = 'Ssmi#th_67'
matricola_studente =  '111190{}'.format(randomString())
matricola_dipendente = '982388{}'.format(randomString())
#  additional_affiliations = [('otherinst.net', 'student', matricola_studente),
                           #  ('othst.gov', 'employee', matricola_dipendente),]
additional_affiliations = []
_test_guy = {'tin': 'abcdef{}'.format(randomString()),
             'surname': 'posto',
             'name': 'pasqualino antani',
             'mail': '{}@yahoo.it'.format(_uid),
             'date_of_birth': get_date_from_string('16/05/1986'),
             'place_of_birth': 'Cosenza',
             #  'affiliation': 'member,student',
             'affiliation': '',
             'gender': 1}

_PURGE_LDAP_TEST_USER = True
_WAIT_FOR_A_CHECK = False


class ProvisioningTestCase(TestCase):
    databases = '__all__'

    def setUp(self):
        # clean up
        self.tearDown()

        d = Identity.objects.create(**_test_guy)
        # additional affiliations
        for addaff in additional_affiliations:
            AdditionalAffiliation.objects.create(identity=d,
                                                 origin=addaff[0],
                                                 name=addaff[1],
                                                 unique_code=addaff[2])

        self.identity = Identity.objects.get(mail=_test_guy['mail'])
        self.provisioning = IdentityProvisioning.objects.create(identity=self.identity)

        # provisioning test
        token_url = self.provisioning.get_activation_url()
        c = Client()
        # test identity creation
        # disable username with prefix constraint
        settings.ACCOUNT_CREATE_USERNAME_PRESET = None
        request = c.post(token_url, {'username': _uid,
                                     'password': _passwd,
                                     'password_verifica': _passwd,
                                     'mail': _test_guy['mail']})
        check = (b'error' in request.content)
        self.assertIs(check, False)

        # check real user existence
        self.ldap_user = LdapAcademiaUser.objects.filter(uid=_uid).first()
        self.assertTrue(self.ldap_user)
        self.assertTrue(self.ldap_user.userPassword)
        self.assertTrue(self.ldap_user.sambaNTPassword)

        # first login
        c = Client()
        lurl = reverse('provisioning:provisioning_login')
        request = c.post(lurl, {'username': _uid,
                                'password': _passwd})
        self.assertEqual(request.status_code, 302)


    def test_print_ldap_user_Attributes(self):
        print('\nCreated User Attributes:\n')
        for k,v in self.ldap_user.__dict__.items():
            if k[0] == '_': continue
            print('\t{}: {}'.format(k, v))


    def test_b_login(self):
        """test account login"""
        c = Client()
        lurl = reverse('provisioning:provisioning_login')
        request = c.post(lurl, {'username': _uid,
                                'password': _passwd})
        self.assertEqual(request.status_code, 302)

    def test_c_password_reset(self):
        """test a password change with confirmation"""
        c = Client()
        lurl = reverse('provisioning:reset_password_ask')
        request = c.post(lurl, {'tin': _test_guy['tin'],
                                'mail': _test_guy['mail']},
                         follow=True,
                         HTTP_ACCEPT_LANGUAGE='en')
        self.assertTrue('You asked for a password reset' in request.content.decode())
        self.assertEqual(request.status_code, 200)
        token = IdentityLdapPasswordReset.objects.last()
        self.assertTrue(token)

        lurl = reverse('provisioning:reset_password_token', kwargs={'token_value': str(token.token)})
        request = c.get(lurl, follow=True,
                        HTTP_ACCEPT_LANGUAGE='en')
        self.assertTrue('renew your password' in request.content.decode())

        d = {'username': _uid,
             'mail': _test_guy['mail'],
             'password': _passwd+_passwd,
             'password_verifica': _passwd+_passwd}
        request = c.post(lurl, d, follow=True, HTTP_ACCEPT_LANGUAGE='en')
        self.assertTrue('Password succesfully changed' in request.content.decode())

    def test_c_password_change(self):
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

    def test_d_changedata(self):
        """test account change identity data"""
        c = Client()
        lurl = reverse('provisioning:provisioning_login')
        request = c.post(lurl, {'username': _uid, 'password': _passwd})
        self.assertEqual(request.status_code, 302)

        lurl = reverse('provisioning:change_data')
        request = c.post(lurl, {'mail': 'ingo_'+_test_guy['mail'],
                                'telephoneNumber': '0984567683'})
        self.assertEqual(request.status_code, 200)
        check = (b'errorlist' in request.content)
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
                                'mail': 'ingo_'+_test_guy['mail']})
        # self.assertEqual(request.status_code, 200)
        self.assertEqual(request.status_code, 302)
        p = IdentityLdapPasswordReset.objects.filter(ldap_dn=d.dn).last()
        token_url = p.get_activation_url()
        request = c.post(token_url, {'username': _uid,
                                     'mail': 'ingo_'+_test_guy['mail'],
                                     'password': _passwd+_passwd,
                                     'password_verifica': _passwd+_passwd})
        self.assertIs(request.status_code, 200)
        # print(request.content)

        if _WAIT_FOR_A_CHECK:
            time.sleep(6000)

    def test_change_username(self):
        user_model = apps.get_model(settings.AUTH_USER_MODEL)
        django_user = user_model.objects.get(username=_uid)
        self.assertFalse(django_user.change_username)
        c = Client()

        # login
        lurl = reverse('provisioning:provisioning_login')
        request = c.post(lurl, {'username': _uid,
                                'password': _passwd})
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

        # login
        lurl = reverse('provisioning:provisioning_login')
        request = c.post(lurl, {'username': _new_uid,
                                'password': _passwd})
        self.assertEqual(request.status_code, 302)

        # try to access to change username page
        # fails: username can be changed only one time
        change_username_url = reverse('provisioning:change_username')
        request = c.get(change_username_url, follow=True)
        self.assertEqual(request.status_code, 403)

        # come back to the previous one
        lu.uid=_uid
        lu.save()

    def test_presetted_usernames_custom_sufx_fails(self):
        settings.ACCOUNT_CREATE_USERNAME_SUFFIX = True
        settings.ACCOUNT_CREATE_USERNAME_SUFFIX_CUSTOMIZABLE = True
        IdentityProvisioning.objects.filter(identity=self.identity).delete()
        provisioning = IdentityProvisioning.objects.create(identity=self.identity)
        # provisioning test
        token_url = provisioning.get_activation_url()
        c = Client()
        req = c.post(token_url, {'username': 'maradona',
                                 'password': _passwd,
                                 'password_verifica': _passwd,
                                 'mail': 'that'+_test_guy['mail']},
                    HTTP_ACCEPT_LANGUAGE='en')
        self.assertTrue('not valid' in req.content.decode())

    def test_presetted_usernames(self):
        settings.ACCOUNT_CREATE_USERNAME_SUFFIX = True
        settings.ACCOUNT_CREATE_USERNAME_SUFFIX_CUSTOMIZABLE = False

        already_used = []
        availables = []
        n_tests = 7
        name_sn = _test_guy['name'], _test_guy['surname']

        for i in get_available_ldap_usernames(name_sn)[:n_tests]:
            for au in already_used:
                availables = get_available_ldap_usernames(name_sn)[:n_tests]
                self.assertFalse(i not in availables)
            print('Available usernames: {}'.format(', '.join(availables)))

            # creating that one
            LdapAcademiaUser.objects.create(uid=i,
                                            givenName=name_sn[0],
                                            sn=name_sn[1],
                                            cn=' '.join(name_sn)
                                            )
            print('Created: {} LDAP account'.format(i))

            IdentityProvisioning.objects.filter(identity=self.identity).delete()
            provisioning = IdentityProvisioning.objects.create(identity=self.identity)

            # provisioning test
            token_url = provisioning.get_activation_url()
            c = Client()
            req = c.post(token_url, {'username': i,
                                     'password': _passwd,
                                     'password_verifica': _passwd,
                                     'mail': randomString()+_test_guy['mail']},
                         HTTP_ACCEPT_LANGUAGE='en')

            self.assertTrue('not valid' not in req.content.decode())

            for au in already_used:
                self.assertFalse('"{}"'.format(au) in req.content.decode())

            already_used.append(i)

        # purge it all
        LdapAcademiaUser.objects.filter(uid__in=already_used).delete()

    def tearDown(self):
        """cleanup"""
        d = LdapAcademiaUser.objects.filter(uid=_uid).first()
        if _PURGE_LDAP_TEST_USER and d:
            d.delete()
            for i in get_available_ldap_usernames(_test_guy['name'],
                                                  _test_guy['surname'])[:9]:
                d = LdapAcademiaUser.objects.filter(uid=i).first()
                if d: d.delete()
