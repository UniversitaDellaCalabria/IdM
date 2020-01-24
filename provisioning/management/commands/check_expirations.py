from django.conf import settings
from django.core.mail import send_mail, mail_admins
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from identity.utils import create_accounts_from_csv
from ldap_peoples.models import LdapAcademiaUser

from provisioning.models import Notifications
from provisioning.utils import (get_default_translations,
                                translate_to)

class Command(BaseCommand):
    help = 'Check Accounts Expirations'

    def add_arguments(self, parser):
        parser.add_argument('-mail', required=False, action="store_true",
                            help="Send alert email to users")
        parser.add_argument('-debug', required=False, action="store_true",
                            help="see debug message")

    def handle(self, *args, **options):
        _debug = options.get('debug')
        l = []
        failed = []
        disabled = []
        from_that_time = timezone.localtime() - timezone.timedelta(days=settings.SHAC_EXPIRY_DURATION_DAYS)

        # disable all the already expired
        exp_ldap_users = LdapAcademiaUser.objects.filter(schacExpiryDate__lte=timezone.localtime())
        print(exp_ldap_users)
        for exp in exp_ldap_users:
            if not exp.pwdAccountLockedTime:
                exp.disable()
                disabled.append(exp.uid)

        ldap_users = LdapAcademiaUser.objects.filter(schacExpiryDate__gt=from_that_time)
        for lu in ldap_users:
            self.stdout.write('Processing {}'.format(lu.dn))
            # check if an email was already sent, otherwise continue to the next loop
            n = Notifications.objects.filter(ldap_dn=lu.dn,
                                             sent=True,
                                             create_date__gt=from_that_time).first()
            if n:
                if _debug: print(lu.uid, 'already sent: {}.'.format(n.create_date))
                continue

            # if not
            # check if the user is renewable, if yes
            if not lu.is_renewable():
                if _debug: print(lu.uid, 'is not renewable.')
                continue

            # check how may days remains before its password expiration
            days = (lu.schacExpiryDate - timezone.localtime()).days

            # if there's still a lot of time...do not send the notification
            if days > settings.EXPIRATION_NOTIFICATION_DAYS_BEFORE:
                if _debug: print(lu.uid, 'still have {} days to renew.'.format(days))
                continue

            if options.get('mail'):
                smd = {'user': lu.uid,
                       'datetime': lu.schacExpiryDate.isoformat(),
                       'days': days,
                       'hostname': settings.HOSTNAME}
                # IDENTITY_PROVISIONING_MSG - two language for everyone!
                mail_subject = get_default_translations(settings.IDENTITY_MSG_EXPIRATION_SUBJECT,
                                                        sep = ' - ')
                mail_body_partlist = [settings.IDENTITY_MSG_HEADER,
                                      settings.IDENTITY_MSG_EXPIRATION_MESSAGE,
                                      settings.IDENTITY_MSG_FOOTER]
                body_translated = []
                for lang in settings.MSG_DEFAULT_LANGUAGES:
                    for i in mail_body_partlist:
                        body_translated.append(translate_to(i, lang))

                msg_body = ''.join(body_translated)
                sent = send_mail(mail_subject,
                                 msg_body.format(**smd),
                                 settings.DEFAULT_FROM_EMAIL,
                                 lu.mail, # this is a list!
                                 fail_silently=True,
                                 auth_user=None,
                                 auth_password=None,
                                 connection=None,
                                 html_message=None)

                n = Notifications.objects.create(ldap_dn=lu.dn,
                                                 remaining_days = days,
                                                 expiration_date=lu.schacExpiryDate)
                if sent:
                    n.sent = True
                    n.save()
                    l.append(lu.uid)
                else:
                    failed.append(lu.uid)

        msg = 'Successfully sent {} notifications'.format(len(l))
        self.stdout.write(self.style.SUCCESS(msg))
        msg = 'Failed {} notifications'.format(len(failed))
        self.stdout.write(self.style.ERROR(msg))
        msg = 'Disabled {} users with pwdAccountLockedTime'.format(len(disabled))
        self.stdout.write(self.style.ERROR(msg))
        if _debug:
            for i in l:
                print('Sent to: ', i)
            for i in failed:
                print('Failed: ', i)
            for i in disabled:
                print('Disabled: ', i)
