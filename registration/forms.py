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
                                  widget=forms.TextInput(attrs={'class': _field_class,
                                                                'placeholder': _("Tax Payer's Identification Number")}))
    mail = forms.EmailField(label="E-mail", max_length=64,
                            help_text=_("name.surname@your.mail.com"),
                            widget=forms.EmailInput(attrs={'class': _field_class,
                                                           'placeholder': _('email@domain.eu')+' ...'}))
    telephoneNumber = forms.CharField(label=_("Telefono"),
                                      min_length=8,
                                      max_length=64,
                                      help_text=_("Your telephone number"),
                                      widget=forms.TextInput(attrs={'class': _field_class,
                                                                    'placeholder': _('Telephone with prefix')}))
