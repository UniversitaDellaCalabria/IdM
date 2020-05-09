from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from identity.admin_inline import *
from identity.models import *
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from .models import *
from . admin_actions import send_activation_email


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


@admin.register(ChangedUsername)
class ChangedUsername(admin.ModelAdmin):
    list_display  = ('old_username', 'new_username', 'create_date')
    list_filter = ('create_date',)
    search_fields = ('old_username', 'new_username')
