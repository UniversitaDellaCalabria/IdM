import pycountry

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


_field_class = "form-control col-xs-12 col-sm-12 col-md-12 col-lg-12"

IMG_PERMITTED_UPLOAD_FILETYPE = getattr(settings,
                                        'IMG_PERMITTED_UPLOAD_FILETYPE',
                                        ("image/jpeg", "image/png",
                                         "image/gif", "image/x-ms-bmp"))
IMG_MAX_UPLOAD_SIZE = getattr(settings, 'IMG_MAX_UPLOAD_SIZE', 10485760)
ATTACH_NAME_MAX_LEN = getattr(settings, 'ATTACH_NAME_MAX_LEN', 50)


class AskForm_1(forms.Form):
    name = forms.CharField(label=_("Name"),
                                  max_length=128,
                                  help_text='',
                                  widget=forms.TextInput(attrs={'class': _field_class,
                                                                'placeholder': _('Name')}))
    surname = forms.CharField(label=_("Surname"),
                                  max_length=128,
                                  help_text='',
                                  widget=forms.TextInput(attrs={'class': _field_class,
                                                                'placeholder': _('Surname')}))

    tin = forms.CharField(label=_("Tax Payer's Identification Number"),
                                  max_length=64,
                                  help_text=_("National identification number"),
                                  widget=forms.TextInput
                                   (attrs={'class': _field_class,
                                           'placeholder': _("Tax Payer's Identification Number")}))
    gender = forms.CharField(label=_('Gender'), initial='',
                                     widget=forms.Select(
                                      choices=(('0', _('Not know')),
                                               ('1', _('Male')),
                                               ('2', _('Female')),
                                               ('9', _('Not specified')))))
    nation_of_birth = forms.CharField(label=_('Nation of Birth'), max_length=3, initial='IT',
                                      widget=forms.Select(
                                       choices=[(e.alpha_2, e.name) for e in pycountry.countries]))
    place_of_birth = forms.CharField(label=_('Place of Birth'),
                                     max_length=50,
                                     widget=forms.TextInput(
                                      attrs={'placeholder': _('Place of Birth')}),
                                      #  help_text=_("If you are Italian please insert your "
                                                  #  "'Comune di nascita' otherwise a human "
                                                  #  "readable Place of Bird")
                                      )
    date_of_birth = forms.DateField(label=_('Date of Birth'),
                                    widget=forms.TextInput(attrs={'type': 'date'}))

    mail = forms.EmailField(label="E-mail", max_length=64,
                            help_text=_("name.surname@your.mail.com"),
                            widget=forms.EmailInput(
                             attrs={'class': _field_class,
                                    'placeholder': _('email@domain.eu')+' ...'}))
    telephoneNumber = forms.CharField(label=_("Mobile Phone"),
                                      min_length=8,
                                      max_length=64,
                                      help_text=_("Mobile phone number"),
                                      widget=forms.TextInput(
                                       attrs={'class': _field_class,
                                              'placeholder': _('Telephone number with prefix')}))
    def clean_tin(self):
        return self.cleaned_data['tin'].upper()

    def clean_date_of_birth(self):
        date = self.cleaned_data['date_of_birth']
        if (timezone.localdate() - date) < timezone.timedelta(days=6205):
            self.add_error('date_of_birth', _("You must be of age"))
        return date

class IdentityDocumentForm(forms.Form):
    document_front = forms.FileField(label=_('Identification Document Front side'))
    document_retro = forms.FileField(label=_('Identification Document Back side'))

    def clean(self):
        cleaned_data = super().clean()
        for field_name in ('document_front', 'document_retro'):
            content = self.cleaned_data.get(field_name)
            # rimuovere caratteri di encoding altrimenti il download fallisce lato ws
            if not content:
                msg = _("An Error occourred, please upload again your document")
                self.add_error(field_name, msg)
                return
            content._name = content._name.encode('ascii',
                                                 errors='ignore').decode('ascii')

            if content.content_type not in IMG_PERMITTED_UPLOAD_FILETYPE:
                msg_tmpl = _("Only these format are permitted: '{}'")
                msg = msg_tmpl.format(', '.join(IMG_PERMITTED_UPLOAD_FILETYPE))
                self.add_error(field_name, msg)
            elif content.size > int(IMG_MAX_UPLOAD_SIZE):
                msg_tmpl = _("Maximum upload size is {}. {} is {}")
                msg = msg_tmpl.format(filesizeformat(MAX_UPLOAD_SIZE),
                                      content._name,
                                      filesizeformat(content.size))
                self.add_error(field_name, msg)
            elif len(content._name) > ATTACH_NAME_MAX_LEN:
                msg_tmpl = _("Maximum filename length is {}")
                msg = msg_tmpl.format(ATTACH_NAME_MAX_LEN,
                                      len(content._name))
                self.add_error(field_name, msg)
