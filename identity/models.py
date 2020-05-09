import pycountry
import os
import uuid

from django.db import models
from django.conf import settings

from model_utils.fields import AutoCreatedField, AutoLastModifiedField
from django.utils.translation import ugettext_lazy as _

from ldap_peoples.idem_affiliation_mapping import (IDEM_AFFILIATION_MAP,
                                                   DEFAULT_AFFILIATION)

from .decorators import is_apps_installed


def _attachment_upload(instance, filename):
    """ this function has to return the location to upload the file """
    return os.path.join('identity_attachments/{}'.format(instance.tin,
                                                         filename))


class TimeStampedModel(models.Model): # pragma: no cover
    """
    self-updating created and modified fields
    """
    created = AutoCreatedField(_('created'), editable=False)
    modified = AutoLastModifiedField(_('modified'), editable=False)

    class Meta:
        abstract = True


class IdentityGenericManyToOne(models.Model):
    name = models.CharField(max_length=256, blank=False, null=False)

    class Meta:
        abstract = True


class IdentityExtendendStatus(models.Model):
    TIPO_CHOICES = (
                    ('de-visu','de-visu'),
                    ('SPID', 'SPID'),
                    ('Esse3', 'Esse3'),
                    ('CSA','CSA'),
                    ('import', _('Import')),
                    )
    flusso = models.CharField(_('Flow'),max_length=135, blank=False,
                              default="", choices=TIPO_CHOICES,
                              help_text=_(("How this entry "
                                           "was created "
                                           "in the DB")))
    descrizione_flusso = models.TextField(_('Flow description'),
                                          blank=True)
    protocollo_numero = models.CharField(_('Record number (Prot.num.)'),
                                         max_length=150,
                                         blank=True, null=True)
    protocollo_anno = models.CharField(_('Record year (Prot. year)'),max_length=4,
                                       blank=True, null=True)
    activation_date = models.DateTimeField(blank=True, null=True,
                                            help_text=_(('When this '
                                                         'identity was '
                                                         'activated')))
    class Meta:
        abstract = True


# TODO tradurre fields
class AbstractIdentityAddress(models.Model):
    address = models.CharField(_('Address'),max_length=150, blank=True, null=True)
    locality_name = models.CharField(_('Locality'),max_length=135, blank=True, null=True)
    state = models.CharField(_('Region'), max_length=60, blank=True, null=True)
    postal_code    = models.CharField(_('Cap'),max_length=60, blank=True, null=True)
    country_name = models.CharField(max_length=128, blank=True, null=True,
                                    help_text=_('Country'))
    note = models.TextField(max_length=768, blank=True, null=True)
    primary =     models.BooleanField(_('Main delivery address'),default=False)
    class Meta:
        #ordering = ['primary',]
        verbose_name_plural = _("Address book")

    def __str__(self):
        return '%s' % (self.identity)


class Identity(IdentityExtendendStatus, TimeStampedModel):
    """
    Provides registry
    """
    personal_title = models.CharField(max_length=12, blank=True, null=True)
    name = models.CharField(max_length=256, blank=False, null=False,
                            help_text=_('Name'))
    surname = models.CharField(max_length=135, blank=False, null=False)
    mail = models.EmailField()
    telephone = models.CharField(max_length=135, blank=True, null=True)
    common_name = models.CharField(max_length=256, blank=True, null=True,
                                   help_text=_('Common Name'))
    #country = CountryField(blank=True, help_text=_('nazionalità, cittadinanza'))
    nation = models.CharField(max_length=3, blank=False, null=True,
                              default='IT', choices=[(e.alpha_2, e.alpha_2)
                                                     for e in pycountry.countries])
    country = models.CharField(max_length=128, blank=True, null=True,
                               help_text=_('Country'))
    city = models.CharField(max_length=128, blank=True, null=True,
                            help_text=_('City'))
    tin = models.CharField(help_text=_('Tax Payer\'s Number or UniqueID'),
                                   max_length=16, blank=False, null=True)
    date_of_birth = models.DateField(blank=False, null=True)
    place_of_birth = models.CharField(max_length=128,
                                      blank=False, null=True, help_text='')
    document_front = models.FileField(help_text=_('Identity card front'),
                                      upload_to=_attachment_upload,
                                      null=True, blank=False)
    document_retro = models.FileField(help_text=_('Identity card retro'),
                                      upload_to=_attachment_upload,
                                      null=True, blank=False)
    affiliation = models.CharField(max_length=128, blank=False, null=True,
                                   help_text=_(("Affiliation")),
                                   choices=[(','.join(v), k)
                                            for k,v in IDEM_AFFILIATION_MAP.items()],
                                   default=list(IDEM_AFFILIATION_MAP.keys())[0])
    description = models.TextField(max_length=1024, blank=True, null=True)

    def is_valid(self):
        """
        Do some test before migrations, is some attributes is needed and other studd
        """
        pass

    class Meta:
        ordering = ['created',]
        verbose_name_plural = _("Digital Identities")

    def __str__(self):
        return '{} {}'.format(self.name, self.surname)


class AdditionalAffiliation(models.Model):
    AFFILIATION = (
                    ('faculty', 'faculty'),
                    ('student', 'student'),
                    ('staff', 'staff'),
                    ('alum', 'alum'),
                    ('member', 'member'),
                    ('affiliate', 'affiliate'),
                    ('employee', 'employee'),
                    ('library-walk-in', 'library-walk-in'),
                  )
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE,
                                 blank=False, null=True)
    name = models.CharField(choices=AFFILIATION,
                            max_length=32)
    unique_code = models.CharField(max_length=64, blank=True,
                                   default='')
    origin = models.CharField(max_length=254, blank=False,
                              default=settings.LDAP_BASE_DOMAIN,
                              help_text=_(('istitution of orgin, where '
                                           'the guest came from')))
    description = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = _("Additional Affiliation")
        verbose_name_plural = _("Additional Affiliations")

    def get_scoped(self):
        return '{}@{}'.format(self.name, self.origin)

    def get_urn(self):
        return ':'.join((settings.SCHAC_PERSONALUNIQUECODE_DEFAULT_PREFIX,
                         self.origin,
                         self.name,
                         self.unique_code))

    @is_apps_installed(['ldap_peoples'])
    def as_shacpersonaluniquecode(self):
        prefix = settings.SCHAC_PERSONALUNIQUECODE_DEFAULT_PREFIX
        return ':'.join((prefix, self.get_urn()))

    def __str__(self):
        return self.name


class IdentityAddress(AbstractIdentityAddress, TimeStampedModel):
    """
    many to one, many addresses to one identity
    """
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE)

    class Meta:
        ordering = ['primary',]
        verbose_name_plural = _("Addresses")
    def __str__(self):
        return '%s %s' % (self.identity, self.primary)


class IdentityCustomAttribute(TimeStampedModel):
    """
    Which Provider contains other attributes related to that identity
    smart generalization for future implementation
    """
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, blank=False,
                            help_text='name of the attribute')
    value = models.TextField(blank=False,
                             help_text='value of the attribute')


class AddressType(models.Model):
    name = models.CharField(max_length=12, blank=False,  null=False,
                            help_text=_(('delivery type as '
                                         'mail, telephone...')),
                            unique=True)
    description = models.CharField(max_length=256, blank=True)
    def __str__(self):
        return '%s' % (self.name)


class IdentityDelivery(TimeStampedModel):
    """
        Generalized contacts classification
        mail, telephone, facebook, twitter
    """
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE)
    type     = models.ForeignKey(AddressType,
                                 blank=False, null=False,
                                 on_delete=models.CASCADE)
    value    = models.CharField(max_length=135, blank=False,  null=False,
                                help_text=_(('mario.rossi@yahoo.it or '
                                             '02 3467457. It depends by the type')))


class IdentityRole(IdentityGenericManyToOne):
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE)


class IdentityAffilitation(IdentityGenericManyToOne):
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE)


class IdentityAttachment(IdentityGenericManyToOne):
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to=_attachment_upload,
                                  null=False,blank=False)
