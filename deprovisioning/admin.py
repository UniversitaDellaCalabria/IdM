from django.contrib import admin
from . models import AccountUpdateLog


@admin.register(AccountUpdateLog)
class AccountUpdateLogAdmin(admin.ModelAdmin):
    list_display  = ('uid', 'event', 'created')
    search_fields = ('uid',)
    list_filter   = ('created',)
