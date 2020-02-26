from django.conf import settings
from django.contrib import auth
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _


def home(request):
    """render the home page"""
    if request.user.is_authenticated: # pragma: no cover
        # return HttpResponseRedirect(reverse(settings.LOGIN_REDIRECT_URL))
        return HttpResponseRedirect(reverse('provisioning:dashboard'))
    return render(request, 'home.html') # pragma: no cover


def maintenance(request):
    """render the home page"""
    return render(request, 'maintenance.html') # pragma: no cover


def test_500(request):
    """render the home page"""
    return render(request, '500.html') # pragma: no cover
