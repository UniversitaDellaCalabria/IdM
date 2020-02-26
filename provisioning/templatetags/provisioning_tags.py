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


@register.filter(name='field_type')
def field_type(field):
    return field.field.widget.__class__.__name__


@register.simple_tag
def new_identity_requestable(request):
    if settings.PROVISONING_REQUEST_ID_APPNAME in settings.INSTALLED_APPS:
        return True
