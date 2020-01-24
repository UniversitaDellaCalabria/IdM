from django.contrib import admin

from .admin_inline import *
from .models import *

# @admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    inlines = [IdentityAttachmentInline,
               IdentityDeliveryInline,
               IdentityAddressInline,
               AdditionalAffiliationInline,
               IdentityProvisioningInline]
    list_display  = ('name', 'surname','email', 'created')
    search_fields = ('name', 'surname','common_name',
                     'email', 'telephone')
    list_filter   = ('created', 'modified',
                     'affiliation',)
    readonly_fields = ('created',
                       'modified',
                       'activation_date',
                       'descrizione_flusso')
    fieldsets = (
                (None, { 'fields' :
                    (  ('personal_title', 'common_name'),
                       ('name', 'surname'),
                       ('email', 'telephone', ),
                       ('nation', 'country', 'city', ),
                       ('fiscal_code',),
                       ('place_of_birth', 'date_of_birth'),
                       ('document_front', 'document_retro',),
                       ('description',),
                       'affiliation',
                    )}),
                ('Informazioni sullo stato', {
                        'classes': ('collapse',),
                        'fields' :
                        (
                            ('flusso', 'descrizione_flusso'),
                            ('protocollo_numero', 'protocollo_anno'),
                            ('activation_date',),
                            ('created', 'modified')
                        )}
                    ),
                )

    #autocomplete_fields = ['country',]
    #actions = [send_email_renew_password,]
    date_hierarchy = 'created'

    class Media:
        js = ('js/textarea-autosize.js',)

class AdditionalAffiliationAdmin(admin.ModelAdmin):
    list_display  = ('identity', 'name', 'origin')
    search_fields = ('name',)
    list_filter   = ('name',)

    class Media:
        js = ('identity/static/js/textarea-autosize.js',)


# @admin.register(AddressType)
class AddressTypeAdmin(admin.ModelAdmin):
    list_display  = ('name', 'description')
    search_fields = ('name',)
    list_filter   = ('name',)

    class Media:
        js = ('identity/static/js/textarea-autosize.js',)
