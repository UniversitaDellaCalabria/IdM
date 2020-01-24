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
        'login',
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
        'change/deliveries/',
        change_deliveries,
        name='change_deliveries',
    ),

    path(
        'change/deliveries/<uuid:token_value>',
        change_deliveries,
        name='change_deliveries_confirm',
    ),

    # re_path(
        # r'^change/deliveries/(?P<token_value>[0-9a-fA-F]{32}\Z)?/?$',
        # change_deliveries,
        # name='change_deliveries'), 

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
