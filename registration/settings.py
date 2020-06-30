from collections import OrderedDict
from django.utils.translation import gettext_lazy as _


REGISTRATION_CAPTCHA_FORM = OrderedDict([
                             ('CaPTCHA',
                              ('CustomCaptchaComplexField',
                               {'label': '',
                                'help_text': '',
                                'pre_text': ''},
                               '')),
                    ]
                )

REGISTRATION_ASK_OBJ = _('Unical ID - Registration request')
REGISTRATION_ASK_BODY = _("""Dear {name},

You have succesfully requested an Account Registration to Università della Calabria.
Please click on the following url to confirm:

{url}

Do not reply to this email,
Regards
""")

ENCRYPTION_SECRET = b'thatsecret'
ENCRYPTION_SALT = b'thatsalt'
