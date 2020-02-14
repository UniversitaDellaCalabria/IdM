from django import template
from django.conf import settings
from django.urls import reverse


register = template.Library()


@register.simple_tag
def login_url():
    return reverse(settings.LOGIN_URLNAME)
