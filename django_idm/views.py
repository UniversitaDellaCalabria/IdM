from django.conf import settings
from django.contrib import auth
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.utils.http import is_safe_url

def home(request):
    """render the home page"""
    if request.user.is_authenticated:
        # return HttpResponseRedirect(reverse(settings.LOGIN_REDIRECT_URL))
        return HttpResponseRedirect(reverse('provisioning:dashboard'))
    # peers = AllowedImportPeer.objects.all()
    d = {}
    return render(request, 'home.html')

def login(request):
    context = {
        "username": '',
        "peer": '',
        "error": "user name e/o password errati"
    }    
    return render(request, "base.html", context=context)
    

    if request.user.is_authenticated:
        referrer = request.META.get('HTTP_REFERER')
        if is_safe_url(referrer):
            return HttpResponseRedirect(referrer)
        return HttpResponseRedirect(reverse(settings.LOGIN_REDIRECT_URL))

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    if sub_system:
        peer = AllowedImportPeer.objects.filter(name=sub_system).first()
        if not peer:
            return HttpResponseRedirect(reverse('home'))
        scoped_username = "{}@{}".format(username, sub_system)
    else:
        peer = None
        scoped_username = username

    if request.method == 'GET':
        return render(request, "login.html", {"peer": peer})

    user = auth.authenticate(username=scoped_username, password=password)
    if user:
        auth.login(request, user)
        return HttpResponseRedirect(reverse(settings.LOGIN_REDIRECT_URL))
    else:
        context = {
            "username": username,
            "peer": peer,
            "error": "user name e/o password errati"
        }
        return render(request, "login.html", context=context)
