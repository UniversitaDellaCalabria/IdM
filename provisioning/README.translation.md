````
./manage.py makemessages -l it

# edit .po file, then
./manage.py compilemessages
````


Example for manual translation
------------------------------

````
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

msgs = []
for lang in ['it', 'en']:
    translation.activate(lang)
    #print(translation.get_language())
    #print(_("created"))
    msgs.append(translation.gettext("created"))
msgs

with translation.override('it'):
    print(_("created"))


from django.conf import settings
settings.IDENTITY_CONFIRMATION_CHANGE_MSG
from provisioning.utils import *
get_default_translations(settings.IDENTITY_CONFIRMATION_CHANGE_MSG)



````
