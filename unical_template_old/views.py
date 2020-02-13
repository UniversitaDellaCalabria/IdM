import logging

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseServerError
from django.views.static import serve
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import is_safe_url

from django.shortcuts import render_to_response, get_object_or_404

# Logging
logger = logging.getLogger(__name__)
hdlr = logging.handlers.SysLogHandler( address = '/dev/log',
                                       facility = logging.handlers.SysLogHandler.LOG_USER )
logger.addHandler( hdlr )
formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
hdlr.setFormatter( formatter )
logger.setLevel( logging.INFO )

def redirect(request):
    return HttpResponseRedirect('http://www.unical.it')

def base_template(request):
    """render the home page"""
    context = {
        "username": '',
        "peer": '',
        "error": "user name e/o password errati"
    }    
    return render(request, "base.html", context=context)

def dashboard_template(request):
    """render the dashboard page"""
    return render(request, "dashboard.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get('next'))

@login_required
def protected_serve(request, path):
    """
    solo i proprietari degli uploads possono scaricare
    """
    document_root = settings.MEDIA_ROOT
    # logger.info(document_root)
    # logger.info(path)
    folders = path.split('/')
    # logger.info(folders)
    # logger.info(request.user.matricola)
    if request.user.matricola in folders:
        logger.info('{} downloaded "{}"'.format(request.user.matricola, path))
        return serve(request, path, document_root=document_root, show_indexes=False)
    return HttpResponseForbidden()

def test_500(request):
    #return HttpResponseServerError()
    return not_existent_var

def error_500(request):
    return render(request, 'custom_500.html', {})
