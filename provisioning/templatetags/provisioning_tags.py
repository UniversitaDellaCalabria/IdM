from django import template
from django.conf import settings
from django.urls import reverse

from provisioning.models import ChangedUsername


register = template.Library()


@register.simple_tag
def login_url():
    return reverse(settings.LOGIN_URLNAME)


@register.simple_tag
def username_changeable(request):
    if ChangedUsername.objects.filter(new_username=request.user.username):
        return False
    else:
        return True
