from django.conf import settings as django_settings
from django.contrib.auth.signals import user_logged_in
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

def notification_access_email(sender, user, request, **kwargs):
    # if access notification email is on
    # works only if this field is active in account model

    user = request.user

    if hasattr(user, 'access_notification'):
        if user.access_notification:
            user_agent = ''
            ipaddress = ''
            if request:
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    try:
                        ipaddress = x_forwarded_for.split(',')[-1].strip()
                    except:
                        pass
                if not ipaddress:
                    ipaddress = request.META.get('REMOTE_ADDR', '')
            d = {'time': timezone.localtime(),
                 'user': user.username,
                 'hostname': django_settings.HOSTNAME,
                 'user_agent': user_agent,
                 'ipaddress': ipaddress}
            send_mail(_('Access notification'),
                      django_settings.IDENTITY_MSG_ACCESS.format(**d),
                      django_settings.DEFAULT_FROM_EMAIL,
                      [user.email, ], # it's a list :)
                      fail_silently=True,
                      auth_user=None,
                      auth_password=None,
                      connection=None,
                      html_message=None)

user_logged_in.connect(notification_access_email)
