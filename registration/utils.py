import importlib
import datetime

from django.conf import settings


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


def serialize_dict(form_cleaned_data):
    serialized_dict = dict()
    for k,v in form_cleaned_data.items():
        if isinstance(v, datetime.date):
            serialized_dict[k] = v.strftime('%Y-%m-%d')
        else:
            serialized_dict[k] = v
    return serialized_dict
