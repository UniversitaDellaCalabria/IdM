import json
import logging
import uuid

from django.core.mail import send_mail, mail_admins
from django.conf import settings
from django.db import models
from django_form_builder.models import DynamicFieldMap
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from identity.models import Identity
from . utils import (get_default_translations,
                     translate_to,
                     get_default_valid_until)


logger = logging.getLogger(__name__)


class AbstractProvisioning(models.Model):
    token = models.UUIDField(unique=True, default=uuid.uuid4,
                             blank=True,
                             help_text="/create/$token")
    sent = models.BooleanField(default=False)
    sent_to = models.CharField(max_length=254, blank=True, null=True)
    sent_date = models.DateTimeField(blank=True, null=True)
    valid_until = models.DateTimeField(blank=True, null=False,
                                       default=get_default_valid_until)
    used = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True,
                                    help_text=_('disable it if needed'))
    create_date = models.DateTimeField(auto_now=True)

    def token_valid(self):
        if (timezone.localtime() > self.valid_until) or \
            not self.is_active or self.used:
            return False
        return True

    def mark_as_used(self):
        self.is_active = False
        self.used = timezone.localtime()
        self.save()

    def get_activation_url(self):
        if hasattr(self, 'identity'):
            return reverse('provisioning:account_create',
                           kwargs={'token_value': self.token })

        elif hasattr(self, 'ldap_dn') and hasattr(self, 'current_data'):
            if 'uid' in self.current_data:
                return reverse('provisioning:change_username_confirm',
                               kwargs={'token_value': self.token})
            return reverse('provisioning:change_data_confirm',
                           kwargs={'token_value': self.token})

        elif hasattr(self, 'ldap_dn'):
            return reverse('provisioning:reset_password_token',
                           kwargs={'token_value': self.token})

        else:
            raise Exception(_(('Not a valid message template found for '
                               'unknown user identity name!')))

    def send_email(self, ldap_user=None, lang=None):
        """
        An email require a token
        """
        if not self.is_active: return False
        d = {'hostname': settings.HOSTNAME,
             'valid_until': self.valid_until}

        if hasattr(self, 'identity'):
            # Account creation
            smd = { 'token_path': self.get_activation_url(),
                    'user': self.identity}
            # IDENTITY_PROVISIONING_MSG - two language for everyone!
            mail_subject = get_default_translations(_('New Account creation'),
                                                    sep = ' - ')

            mail_body_partlist = [settings.IDENTITY_MSG_HEADER,
                                  settings.IDENTITY_PROVISIONING_MSG,
                                  settings.IDENTITY_MSG_FOOTER]

            body_translated = []
            for lang in settings.MSG_DEFAULT_LANGUAGES:
                for i in mail_body_partlist:
                    body_translated.append(translate_to(i, lang))

            msg_body = ''.join(body_translated)
            mails = [self.identity.email,]

        elif hasattr(self, 'ldap_dn') and \
            ldap_user and hasattr(self, 'current_data'):
            # Change confirmation token
            lu = ldap_user

            current_data = json.loads(self.current_data)
            new_data = json.loads(self.new_data)

            f_current_data = ''.join(['{}: {}\n'.format(*i) for i in current_data.items()])
            f_new_data = ''.join(['{}: {}\n'.format(*i) for i in new_data.items()])

            smd = {'token_path':  self.get_activation_url(),
                   'user': lu.uid,
                   'current_data': f_current_data,
                   'new_data': f_new_data}

            # TODO, better code refactor, demand this to a function/method!
            mail_body_partlist = [settings.IDENTITY_MSG_HEADER,
                                  settings.IDENTITY_CONFIRMATION_CHANGE_MSG,
                                  settings.IDENTITY_MSG_FOOTER]
            body_translated = []
            if not lang:
                mail_subject = get_default_translations(_(("Confirmation token: "
                                                           "You requested to change your data")),
                                                        sep=' - ')
                for lang in settings.MSG_DEFAULT_LANGUAGES:
                    for i in mail_body_partlist:
                        body_translated.append(translate_to(i, lang))
            else:
                mail_subject = translate_to(settings.IDENTITY_CONFIRMATION_CHANGE_SUBJ,
                                            lang)
                for i in mail_body_partlist:
                    body_translated.append(translate_to(i, lang))
            msg_body = ''.join(body_translated)
            # END TODO

            # use the new email, otherwise the current one
            mails = [new_data.get('mail')] if new_data.get('mail') else lu.mail

        elif hasattr(self, 'ldap_dn') and ldap_user:
            # Password reset for an existing ldap user
            lu = ldap_user
            smd = {'url': self.get_activation_url(),
                   'token_path':  self.get_activation_url(),
                   'user': lu.uid}
            mail_subject = get_default_translations(settings.IDENTITY_TOKEN_MSG_SUBJECT,
                                                    sep=' - ')
            mail_body_partlist = [settings.IDENTITY_MSG_HEADER,
                                  settings.IDENTITY_RESET_MSG,
                                  settings.IDENTITY_MSG_FOOTER]
            body_translated = []
            if not lang:
                mail_subject = get_default_translations(_(("Confirmation token: "
                                                           "You requested to change your data")),
                                                        sep=' - ')
                for lang in settings.MSG_DEFAULT_LANGUAGES:
                    for i in mail_body_partlist:
                        body_translated.append(translate_to(i, lang))
            else:
                mail_subject = translate_to(settings.IDENTITY_CONFIRMATION_CHANGE_SUBJ,
                                            lang)
                for i in mail_body_partlist:
                    body_translated.append(translate_to(i, lang))
            msg_body = ''.join(body_translated)
            mails = lu.mail
        else:
            raise Exception(_(('Not a valid message template found for '
                               'unknown user identity name!')))

        d.update(smd)
        self.sent = send_mail(mail_subject,
                              msg_body.format(**d),
                              settings.DEFAULT_FROM_EMAIL,
                              mails, # this is a list!
                              fail_silently=True,
                              auth_user=None,
                              auth_password=None,
                              connection=None,
                              html_message=None)
        if self.sent:
            self.sent_to = mails[0]
            self.sent = True
            self.sent_date = timezone.localtime()
            self.save()
            logger.info('Sent email to "{}" OK'.format('; '.join(mails)))
        else:
            logger.info('Send email to "{}" FAILED'.format('; '.join(mails)))
        return self.sent


    class Meta:
        abstract = True


class IdentityProvisioning(AbstractProvisioning):
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE)
    ldap_dn = models.CharField(max_length=254, blank=True, null=True)

    class Meta:
        verbose_name = _('Identity Account Creation token')
        verbose_name_plural = _('Identity Account Creation tokens')

    def __str__(self):
        return '{} {}'.format(self.identity, self.is_active)


class IdentityCreation(models.Model):
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE)
    uid = models.CharField(max_length=128,
                           blank=False, null=False,
                           help_text=_('username choosen by user'))
    ldap_dn = models.CharField(max_length=254,
                               blank=False, null=False)
    create_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Identity Creation')
        verbose_name_plural = _('Identity Creations')

    def __str__(self):
        return '{} {}'.format(self.identity, self.ldap_dn)


class IdentityLdapPasswordReset(AbstractProvisioning):
    ldap_dn = models.CharField(max_length=254)

    class Meta:
        verbose_name = _('Identity Password Reset Token')
        verbose_name_plural = _('Identity Password Reset Tokens')

    def __str__(self):
        return '{} {}'.format(self.ldap_dn, self.is_active)


class IdentityLdapChangeConfirmation(AbstractProvisioning):
    ldap_dn = models.CharField(max_length=254)
    current_data = models.TextField(blank=True, null=False, default='{}')
    new_data = models.TextField(blank=True, null=False, default='{}')

    class Meta:
        verbose_name = _('Identity Ldap Attributes Confirmation Change Token')
        verbose_name_plural = _('Identity Ldap Attributes Confirmation Change Tokens')


class Notifications(models.Model):
    """Notification logs about notification to users"""
    ldap_dn = models.CharField(max_length=254)
    create_date = models.DateTimeField(auto_now=True)
    remaining_days = models.IntegerField(default=0, blank=True)
    expiration_date = models.DateTimeField(blank=True, null=True)
    sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Identity Ldap account expiration Notification')
        verbose_name_plural = _('Identity Ldap account expiration Notifications')


class ChangedUsername(models.Model):
    """Log of the changed username
       You can even define only old_username without a new one
       to blacklist
    """
    new_username = models.CharField(max_length=254,
                                    blank=True, null=True)
    old_username = models.CharField(max_length=254)
    create_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Changed Username')
        verbose_name_plural = _('Changed Usernames')

    def __str__(self):
        return '{} {}'.format(self.old_username, self.create_date)
