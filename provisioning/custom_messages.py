from django.conf import settings
from django.utils.translation import ugettext_lazy as _


INVALID_OPERATION_DISPLAY_TITLE = _("Invalid Action")

INVALID_ACCESS_DISPLAY_TITLE = _("Invalid Access")
INVALID_ACCESS_DISPLAY_MSG = _("You tried to access this resource "
                               "directly. Try to do login first.")
INVALID_ACCESS_DISPLAY_DESC = _("Come back to Home page to "
                                "renew your session")
INVALID_ACCESS_DISPLAY = {'title': INVALID_ACCESS_DISPLAY_TITLE,
                          'avviso': INVALID_ACCESS_DISPLAY_MSG,
                          'description': INVALID_ACCESS_DISPLAY_DESC}

INVALID_TOKEN_DISPLAY_TITLE = _("Resource expired")
INVALID_TOKEN_DISPLAY_MSG = _("This token is expired, "
                              "please ask for another one")
INVALID_TOKEN_DISPLAY = {'title': INVALID_TOKEN_DISPLAY_TITLE,
                         'avviso': INVALID_TOKEN_DISPLAY_MSG,
                         'description': ''}

INVALID_DATA_DISPLAY_TITLE = _("Data not valid")
INVALID_DATA_DISPLAY_MSG = _("Please insert valid data")
INVALID_DATA_DISPLAY = {'title': INVALID_DATA_DISPLAY_TITLE,
                        'avviso': INVALID_DATA_DISPLAY_MSG,
                        'description': ""}

IDENTITY_DISABLED_TITLE = _("Identity disabled")
IDENTITY_DISABLED_MSG = _("You cannot request a password reset")
IDENTITY_DISABLED_DESC = _("Your identity was disabled by "
                           "administrators, please contact our"
                           "technical staff for acknowledge.")
IDENTITY_DISABLED = {'title': IDENTITY_DISABLED_TITLE,
                     'avviso': IDENTITY_DISABLED_MSG,
                     'description': IDENTITY_DISABLED_DESC}


ACCOUNT_SUCCESFULLY_CREATED_TITLE = _("Account succesfully created")
ACCOUNT_SUCCESFULLY_CREATED_MSG = _("Now you can login with your credentials, "
                                    "using the form in the main page")
ACCOUNT_SUCCESFULLY_CREATED = {'title': ACCOUNT_SUCCESFULLY_CREATED_TITLE,
                               'avviso': ACCOUNT_SUCCESFULLY_CREATED_MSG,
                               'description': ""}


ACCOUNT_NOT_EXISTENT_TITLE = _("Invalid Access")
ACCOUNT_NOT_EXISTENT_MSG = _("Your account seems to be disabled or "
                             "not existent. Please renew it or contact "
                             "the technical assistance.")
ACCOUNT_NOT_EXISTENT = {'title': ACCOUNT_NOT_EXISTENT_TITLE,
                        'avviso': ACCOUNT_NOT_EXISTENT_MSG,
                        'description': INVALID_ACCESS_DISPLAY_DESC}

USER_DEFINITION_ERROR_TITLE = _("User definition error")
USER_DEFINITION_ERROR = {'title': USER_DEFINITION_ERROR_TITLE,
                         'avviso': ACCOUNT_NOT_EXISTENT_MSG,
                         'description': INVALID_ACCESS_DISPLAY_DESC}

DATA_CHANGED_TITLE = _("Data succesfully changed")
DATA_CHANGED_MSG = _("Now you can come back to your Dashboard.")
DATA_CHANGED = {'title': DATA_CHANGED_TITLE,
                'avviso': DATA_CHANGED_MSG,
                'description': ""}

USERNAME_SUCCESSIFULLY_CHANGED = {'title': DATA_CHANGED_TITLE,
                                  'avviso': _('Your username has been successfully changed'),
                                  'description': _('Please login with your new username')}
CANNOT_CHANGE_USERNAME = {'title': INVALID_OPERATION_DISPLAY_TITLE,
                         'avviso': _('You are not able to change your username'),
                         'description': _('Contact the administrator')}
NOT_YOUR_USERNAME = {'title': INVALID_OPERATION_DISPLAY_TITLE,
                     'avviso': _('You have inserted a wrong actual username'),
                     'description': _('Please, be carefoul')}
ALREADY_CHANGED_USERNAME = {'title': INVALID_OPERATION_DISPLAY_TITLE,
                            'avviso': _('You have already changed your username'),
                            'description': 'This is a one time operation'}
USERNAME_IN_BLACKLIST = {'title': INVALID_OPERATION_DISPLAY_TITLE,
                         'avviso': _('You have choose a blacklisted or already used username'),
                         'description': 'Please, choose another'}

CONFIRMATION_EMAIL_TITLE = _("A confirmation email was sent")
CONFIRMATION_EMAIL_MSG = _("You have {} minutes to confirm your request")
CONFIRMATION_EMAIL_DESC = _("In the email message you'll find "
                            "a special url (web link) "
                            "that you will use to confirm "
                            "your changes.")
CONFIRMATION_EMAIL = {'title': CONFIRMATION_EMAIL_TITLE,
                       'avviso': CONFIRMATION_EMAIL_MSG.format(settings.CHANGE_CONFIRMATION_EXPIRATION_MINUTES),
                       'description': CONFIRMATION_EMAIL_DESC}

PASSWORD_CHANGED_TITLE = _("Password succesfully changed")
PASSWORD_CHANGED_MSG = _("You're still logged in in "
                         "your previous sessions.")
PASSWORD_CHANGED = {'title': PASSWORD_CHANGED_TITLE,
                    'avviso': PASSWORD_CHANGED_MSG}
                    # 'description': DATA_CHANGED_MSG}

PASSWORD_ASK_RESET_TITLE = _("You asked for a password reset")
PASSWORD_ASK_RESET_MSG = _("If the data you have inserted are valid, "
                           "an email was sent to you.")
PASSWORD_ASK_RESET_DESC = _("In the email message you'll find "
                            "a special url (web link) "
                            "that you will use to renew "
                            "your password.")
PASSWORD_ASK_RESET = {'title': PASSWORD_ASK_RESET_TITLE,
                      'avviso': PASSWORD_ASK_RESET_MSG,
                      'description': PASSWORD_ASK_RESET_DESC}

PASSWORD_SUBMISSION_NOT_VALID_MSG = _("username/email/token combination is wrong")
PASSWORD_SUBMISSION_NOT_VALID_DESC = _("Please check the data "
                                       "you have inserted. "
                                       "If problem persists "
                                       "please contact our "
                                       "thecnical staff.")
PASSWORD_SUBMISSION_NOT_VALID = {'title': INVALID_DATA_DISPLAY_TITLE,
                                 'avviso': PASSWORD_SUBMISSION_NOT_VALID_MSG,
                                 'description': PASSWORD_SUBMISSION_NOT_VALID_DESC}

PASSWORD_ALREADYUSED_MSG = _("It seems that you tried to use a password "
                             "that you already used in the past.")
PASSWORD_ALREADYUSED_DESC = _("This is not permitted, please "
                              "choose a real brand new password.")
PASSWORD_ALREADYUSED = {'title': INVALID_DATA_DISPLAY_TITLE,
                        'avviso': PASSWORD_ALREADYUSED_MSG,
                        'description': PASSWORD_ALREADYUSED_DESC}
