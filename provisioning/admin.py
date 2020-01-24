from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from identity.admin_inline import *
from identity.models import *
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from .models import *
from . admin_actions import send_activation_email



@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    inlines = [
                IdentityAttachmentInline,
                IdentityDeliveryInline,
                IdentityAddressInline,
                AdditionalAffiliationInline,
                IdentityProvisioningInline
               ]
    list_display  = ('name', 'surname','email', 'created')
    search_fields = ('name', 'surname','common_name',
                     'email', 'telephone')
    list_filter   = ('created', 'modified')
    list_filter = (
                   ('created', DateTimeRangeFilter),
                   ('modified', DateTimeRangeFilter),
                   ('activation_date', DateTimeRangeFilter),
                  )
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
    actions = [send_activation_email,]
    date_hierarchy = 'created'

    class Media:
        js = ('js/textarea-autosize.js',)



class AdditionalAffiliationAdmin(admin.ModelAdmin):
    list_display  = ('identity', 'name', 'origin')
    search_fields = ('name',)
    list_filter   = ('name',)

    class Media:
        js = ('identity/static/js/textarea-autosize.js',)


@admin.register(AddressType)
class AddressTypeAdmin(admin.ModelAdmin):
    list_display  = ('name', 'description')
    search_fields = ('name',)
    list_filter   = ('name',)

    class Media:
        js = ('identity/static/js/textarea-autosize.js',)



@admin.register(IdentityProvisioning)
class IdentityProvisioningAdmin(admin.ModelAdmin):
    list_display  = ('identity', 'sent', 'used', 'create_date')
    # search_fields = ('identity', 'surname','common_name', 'email', 'telephone')
    list_filter   = ('sent', 'sent_date', 'create_date', 'used')
    readonly_fields = ('token', 'create_date', #'used',
                       'sent_date', 'sent', 'identity')
    fieldsets = (
                    (None, { 'fields' :
                               (('identity', 'is_active'),
                                ('token', ),
                                ('sent', 'sent_to', 'sent_date', ),
                                ('valid_until', ),
                                ('used', 'ldap_dn'),
                                ('create_date',),
                                )
                           }
                    ),
                )

    #actions = [send_email_renew_password,]
    date_hierarchy = 'create_date'

    # class Media:
        # js = ('js/textarea-autosize.js',)

@admin.register(IdentityLdapPasswordReset)
class IdentityLdapPasswordResetAdmin(admin.ModelAdmin):
    list_display  = ('ldap_dn', 'sent', 'used', 'create_date')
    # search_fields = ('identity', 'surname','common_name', 'email', 'telephone')
    list_filter   = ('sent', 'sent_date', 'create_date', 'used')
    readonly_fields = ('token', 'create_date', 'used',
                       'sent_date', 'sent', 'ldap_dn')
    fieldsets = (
                    (None, { 'fields' :
                               (('ldap_dn', 'is_active'),
                                ('token', ),
                                ('sent', 'sent_to', 'sent_date', ),
                                ('valid_until', ),
                                ('used', ),
                                ('create_date',),
                                )
                           }
                    ),
                )

    #actions = [send_email_renew_password,]
    date_hierarchy = 'create_date'

@admin.register(IdentityLdapChangeConfirmation)
class IdentityLdapChangeConfirmationAdmin(IdentityLdapPasswordResetAdmin):

    fieldsets = [
                    (None, { 'fields' :
                               (('ldap_dn', 'is_active'),
                                ('token', ),
                                ('sent', 'sent_to', 'sent_date', ),
                                ('valid_until', ),
                                ('used', ),
                                ('create_date',),
                                )
                           }
                    ),
                ]

    fieldsets.append((_('Data'), {
                                    'fields': (
                                                ('current_data'),
                                                ('new_data')
                                              )
                                 }
                    ))

    class Media:
        js = ('js/textarea-autosize.js',)


@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    list_display  = ('ldap_dn', 'sent',
                     'expiration_date', 'create_date')
    list_filter = ['expiration_date', 'create_date', 'sent']
