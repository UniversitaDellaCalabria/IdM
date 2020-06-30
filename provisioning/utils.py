import datetime
import random

from django.apps import apps
from django.conf import settings
from django.db import connections
from django.utils import translation, timezone


def get_default_translations(message, sep='\n'):
    messages = []
    for lang in settings.MSG_DEFAULT_LANGUAGES:
        # print(lang)
        translation.activate(lang)
        msg = translation.gettext(message)
        # print(msg)
        messages.append(msg)
    return sep.join(messages)


def translate_to(message, lang='en'):
    translation.activate(lang)
    return translation.gettext(message)


def get_date_from_string(value):
    for f in settings.DATE_INPUT_FORMATS:
        try:
            return datetime.datetime.strptime(value, f)
        except:
            print('Failed: get_date_from_string {}'.format(value))


def get_default_valid_until():
    return timezone.localtime() + \
           timezone.timedelta(minutes=settings.CHANGE_CONFIRMATION_EXPIRATION_MINUTES)


def change_user_username(user, lu, new_username):
    # Update Changed Username list
    cu_model = apps.get_model('provisioning', 'ChangedUsername')
    changed_username = cu_model.objects.create()
    changed_username.old_username = lu.uid
    changed_username.new_username = new_username
    changed_username.save()

    # Update LDAP user uid
    lu.uid = new_username
    lu.save()

    # Update Django user username
    user.username = new_username
    user.dn = lu.dn
    user.save()
    return user


def get_ldapuser_attrs_from_formbuilder_conf(lu):
    if not lu: return {}
    if not hasattr(settings, 'DJANGO_FORM_BUILDER_FIELDS'): return {}
    delivery_dict = {}
    for field_name in settings.DJANGO_FORM_BUILDER_FIELDS:
        if hasattr(lu, field_name):
            attr = getattr(lu, field_name, None)
            if not attr: continue
            delivery_dict[field_name] = attr[0] if isinstance(attr, list) else attr
    return delivery_dict


def get_available_ldap_usernames(elements, sep=None):
    sep = sep or getattr(settings,
                         'ACCOUNT_CREATE_USERNAME_PRESET_SEP', '.')
    preset = sep.join((str(i).lower().replace(' ', '') for i in elements))
    spl_preset = preset.split(sep)
    common_choices = set()
    num_seq = (1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 15, 27)
    if len(spl_preset) > 1:
        for i in num_seq:
            new_username = sep.join((spl_preset[0][:i], spl_preset[1]))
            common_choices.add(new_username)
    # angelo: sn must be always present in the username
    #  for i in num_seq:
        #  common_choices.add(preset[:i])
    choices = list(common_choices)
    for i in range(0, 999):
        for e in tuple(common_choices):
            choices.append('{}{}'.format(e, i))
    ldap_db = connections['ldap']
    ldap_filter = '(|{})'.format(''.join(['(uid={})'.format(i)
                                          for i in choices]))

    result = ldap_db.search_s(settings.LDAP_BASEDN, 2,
                              filterstr=ldap_filter, limit=None)
    lus = [i[1]['uid'][0].decode() for i in result]
    availables = [i for i in choices if i not in lus]
    return availables
