from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import (HttpResponse,
                         Http404,
                         HttpResponseRedirect,
                         HttpResponseNotFound)
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils import translation

from .models import *

def change_language(request, lang):
    request.session['lang'] = lang
    
    # language = get_object_or_404(Lingua, short_name=lang)
    #translation.activate(language.short_name)
    language = translation.get_language_from_request(request)
    translation.activate(language)
    #return HttpResponse( request.META.items())
    #return HttpResponse( request.session.items())

    request.LANGUAGE_CODE = translation.get_language()
    
    # print('translation.get_language_from_request(request)', language)
    current_page = request.META.get('HTTP_REFERER')
    if current_page:
        return HttpResponseRedirect(current_page)
    else:
        return HttpResponseRedirect('/')
