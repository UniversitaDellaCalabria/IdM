from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin

from .models import User
from .admin_inlines import *

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    readonly_fields = ('dn', 'date_joined', 'last_login',)
    list_display = ('username', 'email', 'is_active', 'is_staff', 'is_superuser', )
    list_editable = ('is_active', 'is_staff', 'is_superuser',)
    inlines = [LdapDumpInline, ]
    fieldsets = (
        (None, {'fields': (('dn'),
                           ('username', 'is_active', 'is_staff', 'is_superuser', ),
                           ('password'),

                           )}),
        (_('Change username'), {'fields': (('change_username'),)}),
        (_('Personal data'), {'fields': (( 'first_name', 'last_name'),
                                         ( 'email'),
                                         ('codice_fiscale',),
                                         ('gender', 'place_of_birth',
                                          'birth_date',),
                                        )}),

        (_('Permissions'), {'fields': ('groups', 'user_permissions'),
                            'classes':('collapse',)
                           }),


        (_('System data accesses'), {'fields': (('access_notification',),
                                                ('date_joined',
                                                 'last_login', ),
                                                )
                                    }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
