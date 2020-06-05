import base64
import copy
import logging
import json

from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django_form_builder.enc import encrypt, decrypt

logger = logging.getLogger(__name__)

_captcha = dict(created=timezone.now().isoformat(),
                text="VlGYR")
DATA = dict(name = 'Angelo',
            surname = 'Furfaros',
            tin = 'PPPPpt80a01D086b',
            gender = '1',
            nation_of_birth = 'IT',
            place_of_birth = 'Cosenza',
            date_of_birth = '1980-01-01',
            mail = 'peplinux@yahoo.it',
            telephoneNumber = '2345678987654',
            _hidden_dyn = base64.b64encode(encrypt(json.dumps(_captcha))).decode(),
            _dyn = _captcha['text'])


class RegistrationTestCase(TestCase):
    databases = '__all__'

    def setUp(self):
        """test identity creation"""
        # cleanup
        pass

    def test_registration(self):
        url = reverse('registration:ask')
        c = Client()
        req = c.post(url, DATA, follow=True, HTTP_ACCEPT_LANGUAGE='en')
        self.assertContains(req, 'Congratulation', status_code=200)

    def test_registration_wrong_captcha(self):
        url = reverse('registration:ask')
        c = Client()
        data = copy.copy(DATA)
        data['_dyn'] = '3wetgsd'
        req = c.post(url, data, follow=True)
        self.assertContains(req, 'error', status_code=200)

    def test_registration_wrong_age(self):
        url = reverse('registration:ask')
        c = Client()
        data = copy.copy(DATA)
        data['date_of_birth'] = '2020-01-01'
        req = c.post(url, data, follow=True, HTTP_ACCEPT_LANGUAGE='en')
        self.assertContains(req, 'of age', status_code=200)

    def test_registration_wrong_tin(self):
        url = reverse('registration:ask')
        c = Client()
        data = copy.copy(DATA)
        data['tin'] = '3wetgsd'
        req = c.post(url, data, follow=True, HTTP_ACCEPT_LANGUAGE='en')
        self.assertContains(req, 'TIN code validation failed', status_code=403)

    def test_confirmation(self):
        c = Client()
        token = base64.b64encode(encrypt(json.dumps(DATA))).decode()
        url = reverse('registration:confirm', kwargs={'token': token})
        print('Registration confirmation: {}'.format(url))

        dr = open('unical_template/static/images/logo.png', 'rb')
        df = open('unical_template/static/images/logo.png', 'rb')
        data = dict(document_front = df,
                    document_retro = dr)
        req = c.post(url, data=data, follow=True)
        self.assertIs(req.status_code, 200)
        logger.info('Registration completed!')

    def test_registration_confirmation_colliding_datas(self):
        self.test_registration()
        self.test_confirmation()

        # same email, CF with different digits
        DATA['tin'] = DATA['tin'].upper()
        self.test_registration()

        token = base64.b64encode(encrypt(json.dumps(DATA))).decode()
        url = reverse('registration:confirm', kwargs={'token': token})
        print('Registration confirmation (same email, CF with different digits): {}'.format(url))

        dr = open('unical_template/static/images/logo.png', 'rb')
        df = open('unical_template/static/images/logo.png', 'rb')
        data = dict(document_front = df,
                    document_retro = dr)
        c = Client()
        req = c.post(url, data=data, follow=True, HTTP_ACCEPT_LANGUAGE='en')
        self.assertContains(req, 'already exist', status_code=403)

        # same CF
        DATA['mail'] = 'other@host.it'
        token = base64.b64encode(encrypt(json.dumps(DATA))).decode()
        url = reverse('registration:confirm', kwargs={'token': token})
        print('Registration confirmation (different email, same CF): {}'.format(url))
        data['document_front'].seek(0)
        data['document_retro'].seek(0)
        req = c.post(url, data=data, follow=True, HTTP_ACCEPT_LANGUAGE='en')
        self.assertContains(req, 'already exist', status_code=403)
