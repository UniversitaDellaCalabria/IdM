import datetime

from django.apps import apps
from django.conf import settings
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
