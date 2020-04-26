import re

from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _

from ldap_peoples.models import LdapAcademiaUser
from ldap_peoples.forms import (LdapMultiValuedForm,
                                LdapUserAdminPasswordForm)
from .models import *


_passwd_msg = _('The secret must contains lowercase'
                ' and uppercase characters, '
                ' number and at least one of these symbols:'
                ' !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')

_regexp_pt = r'[A-Za-z0-9!"#$%&\'()*+,-./:;<=>?@\[\\\]^_`{|}~]*'
_field_class = "col-xs-12 col-sm-12 col-md-12 col-lg-12"
_username_widget = forms.TextInput(attrs={'class': _field_class,
                                          'placeholder': _('Username')+' ...'})
_password_widget = forms.PasswordInput(attrs={'class': _field_class,
                                              'placeholder': _('Password')+' ...'})

class IdentityUsernameForm(forms.Form):
    username = forms.CharField(label="", max_length=64,
                               help_text=_("Your username"),
                               widget=_username_widget)

class TelephoneForm(forms.Form):
    telephoneNumber = forms.CharField(label=_("Telefono"),
                                      min_length=8,
                                      max_length=64,
                                      help_text=_("Your telephone number"),
                                      widget=forms.TextInput(attrs={'class': _field_class,
                                                                    'placeholder': _('Telephone with prefix')}))


class IdentityEmailForm(forms.Form):
    mail = forms.EmailField(label="E-mail", max_length=64,
                            help_text=_("name.surname@{} "
                                        "or other email used for registration"
                                        ". ").format(settings.LDAP_BASE_DOMAIN),
                            widget=forms.EmailInput(attrs={'class': _field_class,
                                                           'placeholder': _('email@domain.eu')+' ...'}))


class IdentityLoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=64,
                               widget=_username_widget)
    password = forms.CharField(label="Password",
                               min_length=settings.PPOLICY_PASSWD_MIN_LEN,
                               max_length=settings.PPOLICY_PASSWD_MAX_LEN,
                               validators=[RegexValidator(_regexp_pt,
                                                          message=_passwd_msg)],
                               widget=_password_widget)


class IdentityTokenAskForm(IdentityEmailForm):
    username = forms.CharField(label="Username", required=False,
                           max_length=64,
                           help_text=_("Your username. "
                                       "Leave it blank to receive an "
                                       "email as reminder."),
                           widget=_username_widget)


class PasswordForm(forms.Form):
    password = forms.CharField(label=_("Password"),
                               min_length=settings.PPOLICY_PASSWD_MIN_LEN,
                               max_length=settings.PPOLICY_PASSWD_MAX_LEN,
                               validators=[RegexValidator(_regexp_pt,
                                                          message=_passwd_msg)],
                               widget=_password_widget,
                               help_text=_passwd_msg)
    password_verifica = forms.CharField(label=_("Password verification"),
                                        min_length=settings.PPOLICY_PASSWD_MIN_LEN,
                                        max_length=settings.PPOLICY_PASSWD_MAX_LEN,
                                        validators=[RegexValidator(_regexp_pt,
                                                                   message=_passwd_msg)],
                                        widget=_password_widget,
                                        help_text=_("The same password you "
                                                    "typed before, for verification."))
    def clean_password(self):
        password1 = self.data.get('password')
        password2 = self.data.get('password_verifica')

        if not password2:
            self._errors["password_verifica"] = ErrorList([_("You must confirm your password")])
            return self._errors
        if password1 != password2:
            self._errors['password'] = ErrorList([_("Your passwords do not match")])
            return self._errors

        for regexp in settings.SECRET_FIELD_VALIDATORS.values():
            found = re.findall(regexp, password1)
            if not found:
                raise ValidationError(_passwd_msg)
        return password1

    def clean_password_verifica(self):
        return self.clean_password()


class PasswordChangeForm(PasswordForm):
    field_order = ['old_password', 'password', 'password_verifica']
    old_password = forms.CharField(label=_("Old Password"),
                                   min_length=settings.PPOLICY_PASSWD_MIN_LEN,
                                   max_length=settings.PPOLICY_PASSWD_MAX_LEN,
                                   validators=[RegexValidator(_regexp_pt,
                                                              message=_passwd_msg)],
                                   widget=forms.PasswordInput(attrs={'class': _field_class,
                                                              'placeholder': _('Old Password')+' ...'}),
                                   help_text=_("The password you used to login."))


class AccountCreationForm(PasswordForm, IdentityTokenAskForm):
    username = forms.CharField(label=_('Username'), max_length=64,
                               help_text=_("Your desidered username, if available."),
                               widget=_username_widget)
    token = forms.CharField(widget=forms.HiddenInput())

    def clean_username(self):
        """
        control if a username already exists
        """
        username = self.data.get('username')
        user = LdapAcademiaUser.objects.filter(uid=username)
        if user:
            self._errors["username"] = ErrorList([_("This username already exists, "
                                                    "please use another one.")])
            return self._errors
        # check valid username
        check = re.match('[a-z\.\-0-9\@\_]*', username, re.I)
        if not check or (username != check.group()):
            self._errors["username"] = ErrorList([_("Not a valid Username, "
                                                    "the accepted symbols are:"
                                                    "_ - . @")])
            return self._errors
        return username

    def clean_email(self):
        """
        control if a email already exists
        """
        email = self.data.get('email')
        token = self.data.get('token')
        user = LdapAcademiaUser.objects.filter(mail=email)
        if user:
            self._errors["email"] = ErrorList([_("This email already exists, "
                                                 "cannot create a new identity "
                                                 "with an already used email!")])
            return self._errors
        # check if the email was used for registration (needed)
        registration = IdentityProvisioning.objects.filter(identity__email=email,
                                                           token=token).first()
        if not registration or not registration.token_valid():
            self._errors["email"] = ErrorList([_("Failed to manage your token, "
                                                 "it could have been disabled "
                                                 "or the email you typed was not "
                                                 "linked to any valid registrations.")])
            return self._errors
        return email


class PasswordAskResetForm(IdentityTokenAskForm):
    pass


class PasswordResetForm(PasswordForm, IdentityEmailForm):#, IdentityTokenAskForm):
    username = forms.CharField(label="Username", required=True,
                               max_length=64,
                               widget=_username_widget)

    field_order = ['username', 'mail', 'password', 'password_verifica']


class DeliveryForm(TelephoneForm, IdentityEmailForm):
    pass


class ProfileForm(forms.Form):
    access_notification = forms.BooleanField(required=False,
                                             label=_("Notify accesses via email"),
                                             label_suffix="",
                                             widget=forms.CheckboxInput())


class IdentityUsernameChangeForm(forms.Form):
    old_username = forms.CharField(label=_("Current Username"),
                                    max_length=64, required=True,
                                   widget=_username_widget)
    new_username = forms.CharField(label=_("New Username"),
                                   max_length=64, required=True,
                                   widget=_username_widget)
    confirm_new_username = forms.CharField(label=_("Confirm your new Username"),
                                           max_length=64, required=True,
                                           widget=_username_widget)

    def clean_new_username(self):
        username1 = self.data.get('new_username')
        username2 = self.data.get('confirm_new_username')

        if not username2:
            self._errors["confirm_new_username"] = ErrorList([_("You must re-type new username")])
            return self._errors
        if username1 != username2:
            self._errors['new_username'] = ErrorList([_("Your usernames do not match")])
            return self._errors
        return username2

    def clean_confirm_new_username(self):
        return self.clean_new_username()
