from django.conf import settings
from django.http import (HttpResponse,
                         Http404,
                         HttpResponseForbidden,
                         HttpResponseRedirect,
                         HttpResponseNotFound)
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ldap_peoples.models import LdapAcademiaUser


def valid_ldap_user(func_to_decorate):
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('provisioning:home')+'#login')

        if not request.user.dn:
            return render(request,
                          'custom_message.html',
                          {'title': _(("Invalid Access")),
                           'avviso': _(("You tried to access this resource "
                                        "directly. Try to do login first.")),
                           'description': _(("Come back to Home page to "
                                             "renew your session"))})
        return func_to_decorate(*original_args, **original_kwargs)
    return new_func
