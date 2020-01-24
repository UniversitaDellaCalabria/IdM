"""django_idm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from . import views, settings

admin.site.site_header = 'Amministrazione'
admin.site.site_title  = 'Pannello di amministrazione'

urlpatterns = [
    path('gestione/', admin.site.urls),
    # path('logout', logout, name="logout"),

]

if 'material.frontend' in settings.INSTALLED_APPS:
    from material.frontend import urls as frontend_urls
    urlpatterns.append(
                        url(r'', include(frontend_urls)),
                      )

# Secure media files serve
from django.views.static import serve
from django.contrib.auth.decorators import login_required

if settings.DEBUG:
    # STATICS FILE SERVE
    # from django.views.static import serve
    # urlpatterns.append(
        # path('{}/<path>'.format(settings.STATIC_URL[1:-1]),
            # serve,
            # {'document_root': settings.STATIC_ROOT,
             # 'show_indexes' : True})
    # )

    # MEDIA FILE SERVE
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

else:
    @login_required
    def protected_serve(request, path, document_root=None, show_indexes=False):
        return serve(request, path, document_root, show_indexes)

    urlpatterns.append(
        path('%s<path>.*' % settings.MEDIA_URL[1:], protected_serve, {'document_root': settings.MEDIA_ROOT})
    )
    # end secure media files serve

if 'ldap_peoples' in settings.INSTALLED_APPS:
    import ldap_peoples.urls
    urlpatterns += path('', include(ldap_peoples.urls, namespace='ldap_peoples')),

if 'identity' in settings.INSTALLED_APPS:
    import identity.urls
    urlpatterns += path('', include(identity.urls, namespace='identity')),

if 'provisioning' in settings.INSTALLED_APPS:
    import provisioning.urls
    urlpatterns += path('', include(provisioning.urls, namespace='provisioning')),
