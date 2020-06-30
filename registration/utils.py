import base64
import datetime
import importlib
import json

from django.conf import settings
from django.urls import reverse
from django_form_builder.enc import encrypt


REGISTRATION_ENABLED_CODES = ('stdnum.it.codicefiscale',
                              )


def personal_ids_validators(modules=REGISTRATION_ENABLED_CODES):
    validators = []
    for val in modules:
        element = importlib.util.find_spec(val)
        if element:
            validators.append(element.loader.load_module())
    return validators


def validate_personal_id(value):
    check = False
    for i in personal_ids_validators():
        try:
            if i.validate(value):
                return i.__name__
        except Exception as e:
            pass


def validate_tin(value):
    return validate_personal_id(value)


def serialize_dict(form_cleaned_data):
    serialized_dict = dict()
    for k,v in form_cleaned_data.items():
        if isinstance(v, datetime.date):
            serialized_dict[k] = v.strftime('%Y-%m-%d')
        else:
            serialized_dict[k] = v
    return serialized_dict


def create_registration_token(serialized_dict):
    ser_dict = serialize_dict(serialized_dict)
    enc_value = encrypt(json.dumps(ser_dict))
    return base64.b64encode(enc_value)


def build_registration_token_url(request, token):
    request_path = reverse('registration:confirm', kwargs={'token': token.decode()})
    _offset = request.build_absolute_uri().index('/', 7)
    request_fqdn = '{}{}'.format(request.build_absolute_uri()[:_offset],
                                 request_path)
    return request_fqdn
