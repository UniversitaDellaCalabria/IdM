import importlib

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
