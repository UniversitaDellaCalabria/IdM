import base64
import copy
import logging
import json

from django.test import TestCase, Client
from django.urls import reverse
from django_form_builder.enc import encrypt, decrypt


logger = logging.getLogger(__name__)


DATA = dict(name = 'PeppeTest',
            surname = 'PeppeTest', 
            tin = 'PPPPPT80A01D086B',
            gender = 'M',
            nation_of_birth = 'IT', 
            place_of_birth = 'Cosenza',
            date_of_birth = '1980-01-01',
            mail = 'peppelinux@yahoo.it',
            telephoneNumber = '2345678987654',
            _hidden_dyn = "Z0FBQUFBQmV0c1dLS2NMUXc3VHFxNGZPZ0gtcGdfcEpTdUxNWnJnYVlZOUhzalhsbzY1dWMxMTlqM0lUQkp4b2IwMzEtWTQ0bTA2eUc0eGFkYnZBeXBUNnN3UEdzQTZqS0E9PQ==",
            _dyn = "VlGYR")


class RegistrationTestCase(TestCase):
    databases = '__all__'

    def setUp(self):
        """test identity creation"""
        # cleanup
        pass

    def test_registration(self):
        url = reverse('registration:ask')
        c = Client()
        req = c.post(url, DATA, follow=True)
        self.assertContains(req, 'sent to you', status_code=200)

    def test_registration_wrong_captcha(self):
        url = reverse('registration:ask')
        c = Client()
        data = copy.copy(DATA)
        data['_dyn'] = '3wetgsd'
        req = c.post(url, data, follow=True)
        self.assertContains(req, 'error', status_code=200)

    def test_registration_wrong_tin(self):
        url = reverse('registration:ask')
        c = Client()
        data = copy.copy(DATA)
        data['tin'] = '3wetgsd'
        req = c.post(url, data, follow=True)
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
