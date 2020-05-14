from django.urls import include, path, re_path
from .views import *

app_name = "provisioning"

urlpatterns = [

    path('',
         home,
         name="home"
    ),

    path(
        'create/<uuid:token_value>',
        account_create,
        name='account_create',
    ),

    path(
        'local/login/',
        provisioning_login,
        name='provisioning_login',
    ),

    path(
        'logout',
        provisioning_logout,
        name='provisioning_logout',
    ),

    path(
        'dashboard',
        dashboard,
        name='dashboard',
    ),

    path(
        'change/data/',
        change_data,
        name='change_data',
    ),

    path(
        'change/data/<uuid:token_value>',
        change_data,
        name='change_data_confirm',
    ),

    path(
        'change/username/',
        change_username,
        name='change_username',
    ),

    path(
        'change/username/<uuid:token_value>',
        change_username,
        name='change_username_confirm',
    ),


    # re_path(
        # r'^change/data/(?P<token_value>[0-9a-fA-F]{32}\Z)?/?$',
        # change_data,
        # name='change_data'),

    path(
        'renew/password',
        change_password,
        name='change_password',
    ),

    path(
        'reset/password',
        reset_password_ask,
        name='reset_password_ask',
    ),

    path(
        'reset/password/<uuid:token_value>',
        reset_password_token,
        name='reset_password_token',
    ),

]
