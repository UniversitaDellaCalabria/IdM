from .views import *
from django.urls import include, path

app_name="identity"

urlpatterns = [
    # path(
        # 'radius_renew/<token_value>',
        # renew_radius_password,
        # name='renew-radius-password',
    # ),

    # change language
    path('lang/<lang>', change_language, name='change_language'),

]
