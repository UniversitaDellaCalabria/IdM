from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from . models import *


def send_activation_email(modeladmin, request, queryset):
    """
    used to send activation token for newly created accounts
    """
    cnt_sent = 0
    for i in queryset:
        # if user have already activated it
        id_prov = IdentityProvisioning.objects.filter(identity=i).last()

        if id_prov:
            if not id_prov.token_valid():
                messages.add_message(request, messages.ERROR,
                _('{} {}. Already activated: {}.)'.format(i, i.email, id_prov.used)))
                continue
        else:
            id_prov = create_activation_token(i)
        
        sent = id_prov.send_email()
        if sent:
            messages.add_message(request, messages.INFO,
                                 _('{} {}. Email sent.').format(i, i.email))
            cnt_sent += 1
        else:
            messages.add_message(request, messages.ERROR,
                                 _('{} {}. Email send failed.').format(i,
                                                                       i.email))
    messages.add_message(request, messages.INFO, _('{} sendend Email over {} send requests.').format(cnt_sent, queryset.count()))

send_activation_email.short_description = _("Send Token - Activation Email")
