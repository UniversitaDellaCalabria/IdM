from django.urls import include, path, re_path
from . views import *

app_name = "registration"


urlpatterns = [

    path('ask',
         ask,
         name="ask"
    ),

    path(
        'confirm/<str:token>',
        confirm,
        name='confirm',
    ),

    path(
        'build/token',
        get_registration_token,
        name='get_registration_token',
    ),

    # re_path(
        # r'^change/data/(?P<token_value>[0-9a-fA-F]{32}\Z)?/?$',
        # change_data,
        # name='change_data'),
]
