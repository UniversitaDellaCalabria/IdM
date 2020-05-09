import pycountry

from django import forms
from django.utils.translation import ugettext_lazy as _


_field_class = "form-control col-xs-12 col-sm-12 col-md-12 col-lg-12"


class AskForm_1(forms.Form):
    name = forms.CharField(label=_("Name"),
                                  max_length=128,
                                  help_text=_(""),
                                  widget=forms.TextInput(attrs={'class': _field_class,
                                                                'placeholder': _('Name')}))
    surname = forms.CharField(label=_("Surname"),
                                  max_length=128,
                                  help_text=_(""),
                                  widget=forms.TextInput(attrs={'class': _field_class,
                                                                'placeholder': _('Surname')}))

    tin = forms.CharField(label=_("Tax Payer's Identification Number"),
                                  max_length=64,
                                  help_text=_("National identification number"),
                                  widget=forms.TextInput
                                   (attrs={'class': _field_class,
                                           'placeholder': _("Tax Payer's Identification Number")}))
    gender = forms.CharField(label=_('Gender'),
                                     widget=forms.Select(
                                      choices=(('m', _('Male')),('f', _('Female')),('other', _('Other')))))
    nation_of_birth = forms.CharField(label=_('Nation of Birth'), max_length=3, initial='IT',
                                      widget=forms.Select(
                                       choices=[(e.alpha_2, e.name) for e in pycountry.countries]))
    place_of_birth = forms.CharField(label=_('Place of Birth'),
                                     max_length=50,
                                     widget=forms.TextInput(
                                      attrs={'placeholder': _('"Comune di nascita" or International '
                                                              'identifier')}),
                                      help_text=_("If you are Italian please insert your "
                                                  "'Comune di nascita' otherwise a human "
                                                  "readable Place of Bird"))
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
