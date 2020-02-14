from django import forms
from django.contrib import admin

from .models import *


class LdapDumpForm(forms.ModelForm):
    class Meta:
        model = LdapDump
        fields = "__all__"


class LdapDumpInline(admin.TabularInline):
    form  = LdapDumpForm
    model = LdapDump
    readonly_fields = ('modified', 'dump')
    extra = 0
