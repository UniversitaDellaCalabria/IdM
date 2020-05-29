from django.utils.translation import ugettext_lazy as _

# IDENTITY TOKEN SETTINGS
IDENTITY_TOKEN_EXPIRATION_HOURS = 1
# 168 hours = 7 days
ACCOUNT_CREATION_TOKEN_EXPIRATION_HOURS = 168
CHANGE_CONFIRMATION_EXPIRATION_MINUTES = 30
EXPIRATION_NOTIFICATION_DAYS_BEFORE = 30
IDENTITY_TOKEN_MSG_SUBJECT = _('Unical ID - Token for your Account')

ACCOUNT_CREATE_USERNAME_PRESET = ('name', 'surname')
ACCOUNT_CREATE_USERNAME_PRESET_SEP = '.'

IDENTITY_MSG_HEADER = _("""Dear {user} (your username),
This message was sent to you by https://{hostname}, your IDentity Manager.
Please do not reply to this email.
""")

IDENTITY_MSG_FOOTER = _("""
If you're experiencing in problems please contact our technical staff.
Best regards
""")

IDENTITY_PROVISIONING_MSG = _("""
A new account creation was requested for you.
Please click on the following link and follow the instructions:
https://{hostname}{token_path}

This Token will be valid until: {valid_until}.
If the Token is expired you should ask for a new one.
""")

IDENTITY_RESET_MSG = _("""
A Password reset, regarding {user}, has been requested.
This reset token will be valid until: {valid_until}.

If you want to reset your account password please click on the following link and follow the instructions:
https://{hostname}{token_path}

If the Token is expired you can obtain a new one clicking on "Forgot your password" in the {hostname} main page.
""")

IDENTITY_CONFIRMATION_CHANGE_SUBJ = _("Confirmation token: You requested to change your data")

IDENTITY_CONFIRMATION_CHANGE_MSG = _("""
You have requested to change these data:
{current_data}
to this way:
{new_data}

To confirm these changes you have to click the following link:
https://{hostname}{token_path}

This reset token will be valid until: {valid_until}.
""")

# deprecated, not used anymore
# IDENTITY_MSG_WRONG_EMAIL = _("""{} is tryng to send token to {} instead of {}.\
# Please contact him for assistance!""")

IDENTITY_PASSWORD_SUCCESFULL_CHANGED = _("""
Your password was succesfully changed.
It will be valid until: {password_expiration}.

If you need to change it again remember that this will be always possibile
using "Forgot your password" section in {hostname} main page.

Regards
""")

IDENTITY_MSG_ACCESS = _("""Dear {user} (your username),
You have accessed to https://{hostname} at: {time}.

With this Web Browser (user-agent):
{user_agent}

And this IP Address:
{ipaddress}

If it was not you and think that someone could have steal your credentials,
please renew your password through the website section called "Forgot your Password".
""")

IDENTITY_MSG_EXPIRATION_SUBJECT = _('Unical ID - Password expiration')

IDENTITY_MSG_EXPIRATION_MESSAGE = _("""Your password will expire in date: {datetime}.
You have {days} days to renew it, if this period will pass you can
click on "Forgot your Password" section, in https://{hostname}.
""")


# emails will be sent in these languages by default
MSG_DEFAULT_LANGUAGES = ('it', 'en')
