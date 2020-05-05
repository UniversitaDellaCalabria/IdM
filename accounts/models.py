from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class User(AbstractUser):
    GENDER= (( 'male', _('Male')),
             ( 'female', _('Female')),
             ( 'other', _('Other')),)

    dn = models.CharField(blank=True, default='',
                          max_length=254)
    is_active = models.BooleanField(_('active'), default=True)
    email = models.EmailField('email address', blank=True, null=True)
    first_name = models.CharField(_('Name'), max_length=30, blank=True, null=True)
    last_name = models.CharField(_('Surname'), max_length=30, blank=True, null=True)
    codice_fiscale = models.CharField(_('TIN - Tax payer\'s Identification number'),
                                      max_length=50,
                                      blank=True, null=True)
    gender = models.CharField(_('Gender'), choices=GENDER,
                              max_length=12, blank=True, null=True)
    place_of_birth = models.CharField(_('Place of birth'),
                                      max_length=30, blank=True, null=True)
    
    birth_date = models.DateField(_('Date of birth'), null=True, blank=True)
    access_notification = models.BooleanField(_('Send Email notification accesses'),
                                              default=True,
                                              help_text="enable email send")
    change_username = models.BooleanField(_('Allow user to change his username'),
                                          default=False)

    class Meta:
        ordering = ['username']
        verbose_name_plural = ' '.join((_("Users"), settings.APP_NAME))

    def __str__(self): # pragma: no cover
        return '{}'.format(self.first_name)


class LdapDump(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    dump = models.TextField(_('Json attributes'), blank=False, null=False)
    modified = models.DateTimeField(auto_now_add=True)

    def __str__(self): # pragma: no cover
        return '{} {}'.format(self.user.first_name,
                              self.user.last_name)
