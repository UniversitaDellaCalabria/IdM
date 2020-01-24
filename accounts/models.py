from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType

from django.conf import settings


class User(AbstractUser):
    GENDER= (
                ( 'male', _('Male')),
                ( 'female', _('Female')),
                ( 'other', _('Other')),
            )
    
    dn = models.CharField(blank=True, default='',
                          max_length=254)
    is_active = models.BooleanField(_('active'), default=True)
    email = models.EmailField('email address', blank=True, null=True)
    matricola = models.CharField(_('Matricole/Identification number')
                                 , max_length=6, 
                                 blank=True, null=True,
                                 help_text="")
    first_name = models.CharField(_('Name'), max_length=30, blank=True, null=True)
    last_name = models.CharField(_('Surname'), max_length=30, blank=True, null=True)   
    codice_fiscale = models.CharField(_('Fiscal code'), max_length=16, 
                                      blank=True, null=True)  
    gender    = models.CharField(_('Gender'), choices=GENDER, max_length=12, blank=True, null=True)
    location = models.CharField('Place of birth', max_length=30, blank=True, null=True)
    birth_date = models.DateField('Date of birth', null=True, blank=True)
    
    # short_description = models.CharField(_('Descrizione breve'), max_length=33, blank=True, null=True)    
    # bio = models.TextField('Biografia, note', max_length=2048, blank=True, null=True)
    # avatar  = models.ImageField('Avatar, foto', upload_to='avatars/', null=True, blank=True)
    # webpage_url = models.CharField(_('Pagina web'), max_length=512, blank=True, null=True)    

    access_notification = models.BooleanField(_('Send Email notification accesses'), default=True,
                                              help_text="enable email send")

    class Meta:
        ordering = ['username']
        verbose_name_plural = ' '.join((_("Users"), settings.APP_NAME))
    
    def __str__(self):
        return '%s - %s %s' % (self.matricola,
                               self.first_name, self.last_name)
