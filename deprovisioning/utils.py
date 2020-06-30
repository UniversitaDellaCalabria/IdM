import logging

from csa_api import CsaConnect
from django.conf import settings
from unie3api.unie3api import uniE3Api

csaconn = CsaConnect(settings.CSA_API_BASE_URL,
                     token=settings.CSA_API_TOKEN )
e3 = uniE3Api(settings.ESSE3_API_URL,
              settings.ESSE3_API_TOKEN)
logger = logging.setLogger(__name__)


def add_student_attrs(ldap_user):
    pass


def remove_student_attrs(ldap_user):
    pass


def remove_membership(ldap_user):
    pass


def add_employee_attrs(ldap_user):
    pass


def remove_employee_attrs(ldap_user):
    pass


def upgrade_user_profile(ldap_user):
    cf = None
    for uniqueid in ldap_user.schacPersonalUniqueID:
        if 'it:cf' in uniqueid.lower():
            cf = uniqueid
            break
    if not cf:
        logger.error('Upgrade user profile error: cannot find any usable '
                     'schacPersonalUniqueID for {}'.format(ldap_user.dn))
        return

    cf = cf.split(':')[-1]

    student_status = {}
    employee_status = {}
    try:
        student_status = e3.attivo(cf)
    except Exception as e:
        e3 = uniE3Api(settings.CSA_API_URL, settings.CSA_API_TOKEN)
        student_status = e3.attivo(cf)

    try:
        employee_status = csaconn.attivo(cf)
    except Exception as e:
        csaconn = CsaConnect(settings.CSA_API_BASE_URL,
                             token=settings.CSA_API_TOKEN)
        csaconn.auth()
        employee_status = csaconn.attivo(cf)

    if student_status:
        add_student_attrs(ldap_user)
    else:
        remove_student_attrs(ldap_user)

    if employee_status:
        add_employee_attrs(ldap_user)
    else:
        remove_employee_attrs(ldap_user)

    if not all((employee_status, student_status)):
        remove_membership(ldap_user)

    return {'student_status': student_status,
            'employee_status': employee_status}
