from django import forms
from django.contrib import admin

from .models import *
from provisioning.models import IdentityProvisioning

class IdentityProvisioningForm(forms.ModelForm):
    class Meta:
        model = IdentityProvisioning
        fields = ('__all__')

class IdentityProvisioningInline(admin.StackedInline):
    form  = IdentityProvisioningForm
    model = IdentityProvisioning
    readonly_fields = ('token', 'create_date', 'sent_date',
                       'sent', 'identity', 'used')
    fieldsets = (
                    (None, { 'fields' :
                               (('identity', 'is_active'),
                                ('token', ),
                                ('sent', 'sent_date'),
                                ('valid_until',),
                                ('used',),
                                ('create_date',))
                           }
                    ),
                )
    extra = 0

class IdentityAddressForm(forms.ModelForm):
    class Meta:
        model = IdentityAddress
        fields = ('__all__')

class IdentityAddressInline(admin.StackedInline):
    form  = IdentityAddressForm
    model = IdentityAddress
    extra = 0

class IdentityDeliveryForm(forms.ModelForm):
    class Meta:
        model = IdentityDelivery
        fields = ('__all__')

class IdentityDeliveryInline(admin.StackedInline):
    fields = (('type', 'value'),)
    form  = IdentityDeliveryForm
    model = IdentityDelivery
    extra = 0

# class IdentityRadiusAccountForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
        # super(IdentityRadiusAccountForm, self).__init__(*args, **kwargs)
        # self.fields['radius_account'].queryset = RadiusCheck.objects.filter(is_active=True).order_by('-created')

        # instance = getattr(self, 'instance', None)
        # if instance and instance.pk:
            # self.fields['token'].widget.attrs['readonly'] = True
            # self.fields['token'].widget.attrs['size'] = 29
            # self.fields['token'].widget.attrs['disabled'] = True

    # class Meta:
        # model = IdentityRadiusAccount
        # fields = ('__all__')

class IdentityAttachmentInline(admin.StackedInline):
    fields = (('name', 'attachment'),)
    model = IdentityAttachment
    extra = 0
    #autocomplete_fields = ['radius_account',]


class AdditionalAffiliationInline(admin.StackedInline):
    #form  = IdentityAddressForm
    fields = (
                ('name', 'origin', 'unique_code'),
                'description',
                )
    model = AdditionalAffiliation
    extra = 0
