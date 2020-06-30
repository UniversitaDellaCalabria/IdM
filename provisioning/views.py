import copy
import json
import logging
import ldap
import random
import string

from collections import OrderedDict
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, mail_managers
from django.db.models import Q
from django_form_builder.models import SavedFormContent
from django_form_builder.utils import get_labeled_errors
from django.http import (HttpResponse,
                         Http404,
                         HttpResponseForbidden,
                         HttpResponseRedirect,
                         HttpResponseNotFound)
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.module_loading import import_string
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from . custom_messages import *
from . decorators import *
from . forms import *
from . models import *
from . utils import (change_user_username,
                     get_ldapuser_attrs_from_formbuilder_conf,
                     translate_to)

from ldap_peoples.models import LdapAcademiaUser


logger = logging.getLogger(__name__)


def account_create(request, token_value):
    id_prov = get_object_or_404(IdentityProvisioning, token=token_value)
    if not id_prov.token_valid():
        return render(request, 'custom_message.html',
                      INVALID_TOKEN_DISPLAY, status=403)
    d = {'APP_NAME': settings.APP_NAME}

    # USERNAME PRESETS
    username_preset = ''
    if getattr(settings, 'ACCOUNT_CREATE_USERNAME_PRESET', None):
        elements = [getattr(id_prov.identity, i).lower().replace(' ', '')
                    for i in settings.ACCOUNT_CREATE_USERNAME_PRESET]
        username_preset = settings.ACCOUNT_CREATE_USERNAME_PRESET_SEP.join(elements)
        initial={'token': token_value, 'username': username_preset}
        #  import pdb; pdb.set_trace()
        if getattr(settings, 'ACCOUNT_CREATE_USERNAME_SUFFIX', False):
            if getattr(settings, 'ACCOUNT_CREATE_USERNAME_SUFFIX_CUSTOMIZABLE', False):
                account_creation_form = AccountCreationPresettedSuffixedForm
                initial['username_suffix'] =  '-'+''.join(random.choice(string.ascii_lowercase)
                                                          for x in range(4))
                form = account_creation_form(initial=initial)
            else:
                account_creation_form = AccountCreationSelectableUsernameForm
                get_available_ldap_usernames_name = settings.ACCOUNT_CREATE_USERNAME_CREATION_FUNC
                get_available_ldap_usernames = import_string(get_available_ldap_usernames_name)

                # filter out blacklisted and already used in the past usernames
                usernames = [i for i in get_available_ldap_usernames(elements)
                             if not ChangedUsername.objects.filter(Q(new_username=i)|
                                                                   Q(old_username=i))]
                initial['username'] = usernames
                form = account_creation_form(initial=initial)
                form.fields['username'].choices = ((i,i) for i in usernames)
    else:
        initial={'token': token_value}
        account_creation_form = AccountCreationForm
        form = account_creation_form(initial=initial)

    if request.method == 'GET':
        d['form'] = form
        return render(request, 'account_create.html', d)

    elif request.method == 'POST':
        data = request.POST.copy()
        data['token'] = token_value
        form = AccountCreationForm(data)
        d['form'] = form

        if not all((form.username_preset_validator(username_preset),
                    form.is_valid())):
            return render(request, 'account_create.html', d)

        if data['token'] != id_prov.token or \
           data['mail'] != id_prov.identity.mail:
               return render(request, 'custom_message.html',
                             INVALID_DATA_DISPLAY, status=403)

        # TODO, gestire title (multivalued) LDAP qui!
        entry = {'uid' : form.cleaned_data['username'],
                 'cn' : id_prov.identity.name,
                 'givenName' : id_prov.identity.name,
                 'sn' : id_prov.identity.surname,
                 'displayName' : ' '.join((id_prov.identity.name,
                                           id_prov.identity.surname)),
                 'mail' : [form.cleaned_data['mail']],
                 'telephoneNumber' : [id_prov.identity.telephoneNumber,],
                 'eduPersonAssurance': settings.EDUPERSON_DEFAULT_ASSURANCE,
                 'schacGender' : id_prov.identity.gender,
                 'schacPlaceOfBirth' : ','.join((id_prov.identity.nation_of_birth,
                                                 id_prov.identity.place_of_birth)),
                 'schacDateOfBirth' : id_prov.identity.date_of_birth,
                 #  'schacHomeOrganization' : settings.SCHAC_HOMEORGANIZATION_DEFAULT,
                 #  'schacHomeOrganizationType': settings.SCHAC_HOMEORGANIZATIONTYPE_DEFAULT
                 #  'eduPersonPrincipalName': '@'.join((form.cleaned_data['username'],
                                                     #  settings.LDAP_BASE_DOMAIN)),
                 }

        ldap_user = LdapAcademiaUser(**entry)
        ldap_user.set_schacPersonalUniqueID(value=id_prov.identity.tin.upper(),
                                            country_code=id_prov.identity.nation_of_birth.lower())

        # IDENTITY AFFILIATIONS
        if id_prov.identity.affiliation:
            ldap_user.eduPersonAffiliation = id_prov.identity.affiliation.split(',')
            eduPersonScopedAffiliation = [aff+'@'+settings.SCHAC_HOMEORGANIZATION_DEFAULT
                                          for aff in ldap_user.eduPersonAffiliation
                                          if aff]
        # IDENTITY additionals affiliations
        addaff = id_prov.identity.additionalaffiliation_set.all()
        if addaff:
            additional_affiliations = [aff.get_scoped()
                                       for aff in addaff if aff]
            eduPersonScopedAffiliation.extend(additional_affiliations)
            ldap_user.eduPersonScopedAffiliation = eduPersonScopedAffiliation

            # additional personal unique codes from additionals affiliations
            ldap_user.schacPersonalUniqueCode = [aff.get_urn() for aff in addaff]
            ldap_user.set_default_schacExpiryDate()

        # save before change the password
        try:
            ldap_user.save()
        except ldap.CONSTRAINT_VIOLATION as e:
            logging.error('Account Creation Failed: User submitted a '
                          'unique information already used by another account.')
            _msg = {'title': _("Invalid Data"),
                    'avviso': _("It seems that you are already registered"),
                    'description': _('Please go in the Home Page and activate '
                                'the "Forgot your Password" procedure')}
            return render(request, 'custom_message.html', _msg, status=403)
        except Exception as e:
            error_mail_obj = _('Something goes wrong with the account creation')
            error_mail_body = 'Account Creation FAILED for {}: {}.\n Data: {}\n Identity: {}'\
                                .format(ldap_user.dn, e,
                                        ldap_user.__dict__, id_prov.identity.__dict__)
            logger.error(error_mail_body)
            mail_managers(error_mail_obj, error_mail_body)
            _msg = {'title': error_mail_obj,
                    'avviso': _('The data you have submitted produced a validation error.'),
                    'description': _('An email was sent to the technical staff')}
            return render(request, 'custom_message.html', _msg, status=403)

        # altrimenti mi fallisce lo unit test!
        ldap_user.set_password(form.cleaned_data['password'])

        id_prov.mark_as_used()
        id_prov.identity.activation_date = timezone.localtime()
        id_prov.identity.save()

        logger.info('Account created {}'.format(ldap_user.dn))
        return render(request,
                      'custom_message.html',
                      ACCOUNT_SUCCESFULLY_CREATED)


def home(request):
    """render the home page"""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('provisioning:dashboard'))
    d = {'password_reset_form' : PasswordAskResetForm()}
    return render(request, 'home.html', d)


def provisioning_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('provisioning:home'))


def provisioning_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('provisioning:dashboard'))

    if request.method == 'POST':
        login_form = IdentityLoginForm(request.POST)
        if not login_form.is_valid():
            return render(request,
                          'provisioning_login.html',
                          {'login_form': login_form})
        username = login_form.cleaned_data['username']
        password = login_form.cleaned_data['password']
        user = authenticate(request,
                            username=username,
                            password=password)
        if user:
            login(request, user)
            logger.info('Login of {} directly via LDAP'.format(user))
            if request.POST.get('next'):
                return HttpResponseRedirect(request.POST.get('next'))
            return HttpResponseRedirect(reverse('provisioning:dashboard'))
        else:
            messages.add_message(request, messages.ERROR,
                                 _("Invalid Username or Password"))
            return render(request, 'provisioning_login.html',
                                   {'login_form': login_form})
    else:
        # login form if method == 'GET'
        d = {'login_form': IdentityLoginForm()}
        return render(request,
                      'provisioning_login.html', d)


def get_ldapuser_aai_html_attrs(lu):
    hidden_attributes = ['memberOf',
                         'userPassword',
                         'sambaNTPassword',
                         'creatorsName',
                         'modifiersName',
                         'pwdHistory',
                         'pwdAccountLockedTime',
                         'base_dn',
                         'dn']
    attributes = OrderedDict()
    for k in sorted(lu.__dict__.keys()):
        if k[0] == '_' or k in hidden_attributes:
            continue
        attributes[k] = lu.__dict__[k]
    for k,v in attributes.items():
        if isinstance(v, list):
            attributes[k] = '<br>'.join(v)
    return attributes


@login_required
def dashboard(request):
    d = {}
    if request.user.dn:
        try:
            lu = LdapAcademiaUser.objects.filter(dn=request.user.dn).first()
        except ldap.NO_SUCH_OBJECT as e:
            _msg = 'request.user {} authenticated but his DN dows not match with {}.'.format(request.user, request.user.dn)
            logger.error(_msg)
            return render(request,
                          'custom_message.html',
                          USER_DEFINITION_ERROR,
                          status=500)
        if not lu:
            return render(request,
                          'custom_message.html',
                          USER_DEFINITION_ERROR,
                          status=403)

        if not lu.schacExpiryDate:
            lu.set_default_schacExpiryDate()

        delivery_dict = get_ldapuser_attrs_from_formbuilder_conf(lu)
        dyn_form = SavedFormContent.compiled_form(data_source=json.dumps(delivery_dict),
                                                  constructor_dict=settings.DJANGO_FORM_BUILDER_FIELDS,
                                                  ignore_format_field_name=True)
        d = {'form_delivery': dyn_form,
             'password_reset_form': PasswordChangeForm(),
             'form_profile': ProfileForm(initial={'access_notification': \
                                                  request.user.access_notification}),
             'lu': lu,
             'attrs': get_ldapuser_aai_html_attrs(lu),
             'expiration_days': (lu.schacExpiryDate - timezone.localtime()).days}
        return render(request, 'dashboard.html', d)
    return render(request, 'empty_dashboard.html')


@login_required
@valid_ldap_user
def change_data(request, token_value=None):
    lu = LdapAcademiaUser.objects.filter(dn=request.user.dn).first()
    if request.method == 'GET' and token_value:
        # check token validity and commit changes
        id_prov = get_object_or_404(IdentityLdapChangeConfirmation,
                                    token=token_value)
        if not id_prov.token_valid():
            return render(request,
                          'custom_message.html',
                          INVALID_TOKEN_DISPLAY, status=403)

        data = json.loads(id_prov.new_data)
        if 'access_notification' in data.keys():
            request.user.access_notification = data.pop('access_notification')
            request.user.save()

        for i in data:
            if not hasattr(lu, i): continue
            attr = getattr(lu, i)
            if isinstance(attr, list):
                if attr:
                    attr[0] = data[i]
                else:
                    attr.append(data[i])
            else:
                setattr(lu, i, data[i])
        try:
            lu.save()
            id_prov.mark_as_used()
        except ldap.CONSTRAINT_VIOLATION:
            logger.error(_('Error, {} tried to save data that violates a '
                           'LDAP constraint with : {}').format(lu, json.dumps(data)))
            return render(request,
                          'custom_message.html',
                          DATA_NOT_CHANGED, status=403)

        return render(request,
                      'custom_message.html',
                      DATA_CHANGED)

    elif request.method == 'POST':
        form = SavedFormContent.compiled_form(data_source=json.dumps(request.POST),
                                              constructor_dict=settings.DJANGO_FORM_BUILDER_FIELDS,
                                              ignore_format_field_name=True)
        d = {'form_delivery': form,
             'form_password': PasswordForm(),
             'form_profile': ProfileForm(initial={'access_notification': \
                                                  request.user.access_notification}),
             'lu': lu,
             'attrs': get_ldapuser_aai_html_attrs(lu)}

        if not form.is_valid():
            for k,v in get_labeled_errors(form).items():
                messages.add_message(request, messages.ERROR,
                                     "<b>{}</b>: {}".format(k, strip_tags(v)))
            return render(request, 'dashboard.html', d)

        # create token
        current_data = {}
        new_data = {k:v for k,v in form.cleaned_data.items()}
        for k in form.cleaned_data:
            if hasattr(lu, k): attr = getattr(lu, k)
            else: del new_data[k]
            if isinstance(attr, list):
                current_data[k] = attr[0] if attr else []
            else:
                current_data[k] = attr

        # profile options
        form_profile = ProfileForm(request.POST)
        if not form_profile.is_valid():
            return render(request, 'dashboard.html', d)

        access_notification = form_profile.cleaned_data.get('access_notification')
        # Exclude processing if data aren't changed
        if request.user.access_notification != access_notification:
            new_data['access_notification'] = access_notification
            current_data['access_notification'] = request.user.access_notification

        # data was not changed
        if current_data == new_data or not new_data:
            messages.add_message(request, messages.SUCCESS, _("No data edited"))
            return redirect('provisioning:dashboard')

        data = dict(ldap_dn = lu.dn,
                    is_active = True,
                    current_data = json.dumps(current_data),
                    new_data = json.dumps(new_data))
        data_check = {k:v for k,v in data.items()}
        id_change_conf = IdentityLdapChangeConfirmation.objects.filter(**data_check).first()
        if not id_change_conf or not id_change_conf.token_valid():
            id_change_conf = IdentityLdapChangeConfirmation.objects.create(**data)
            # send_email here. Only on creation
            id_change_conf.send_email(ldap_user=lu,
                                      lang=request.LANGUAGE_CODE)
        # messages.add_message(request, messages.SUCCESS,
                             # settings.MESSAGES_ALERT_TEMPLATE_DESC.format(**CONFIRMATION_EMAIL))
        # return redirect('provisioning:dashboard')
        return render(request,
                      'custom_message.html',
                      CONFIRMATION_EMAIL)
    else:
        return render(request,
                      'custom_message.html',
                      INVALID_DATA_DISPLAY, status=403)


@login_required
@valid_ldap_user
def change_username(request, token_value=None):
    """
    Ask a token to change his username
    """
    _err_msg = None
    if not request.user.change_username:
        _err_msg = CANNOT_CHANGE_USERNAME
    elif ChangedUsername.objects.filter(Q(new_username=request.user.username)|
                                        Q(old_username=request.user.username)):
        _err_msg = ALREADY_CHANGED_USERNAME
    if _err_msg:
        return render(request, 'custom_message.html', _err_msg, status=403)

    lu = LdapAcademiaUser.objects.filter(dn=request.user.dn).first()
    if request.method == 'GET' and token_value:
        # check token validity and commit changes
        id_prov = get_object_or_404(IdentityLdapChangeConfirmation,
                                    token=token_value)
        if not id_prov.token_valid():
            return render(request,
                          'custom_message.html',
                          INVALID_TOKEN_DISPLAY, status=403)
        data = json.loads(id_prov.new_data)

        # logout first
        user = get_user_model().objects.get(username=request.user.username)
        logout(request)

        # Change username, uid and create a ChangedUsername record
        user = change_user_username(user=user,
                                    lu=lu,
                                    new_username=data['uid'])
        id_prov.mark_as_used()

        # Logout and redirect to login page
        #
        messages.add_message(request, messages.SUCCESS,
                             settings.MESSAGES_ALERT_TEMPLATE_DESC.format(**USERNAME_SUCCESSIFULLY_CHANGED))
        return redirect('provisioning:provisioning_login')
    elif request.method == 'GET':
        return render(request,
                      'provisioning_change_username.html',
                      dict(change_username_form=IdentityUsernameChangeForm()))
    elif request.method == 'POST':
        form = IdentityUsernameChangeForm(request.POST)
        if form.is_valid():
            old_username = form.cleaned_data['old_username']
            new_username = form.cleaned_data['new_username']

            user_username_match = old_username == request.user.username
            lu_uid_match = old_username == lu.uid

            _err_msg = None
            # If lu.uid and user.username don't match
            if not user_username_match or not lu_uid_match:
                _err_msg = settings.MESSAGES_ALERT_TEMPLATE_DESC.format(**NOT_YOUR_USERNAME)
            # If user has already changed
            elif ChangedUsername.objects.filter(new_username=lu.uid):
                _err_msg = settings.MESSAGES_ALERT_TEMPLATE_DESC.format(**ALREADY_CHANGED_USERNAME)
            # If new username is in blacklist
            elif ChangedUsername.objects.filter(old_username=new_username):
                _err_msg = settings.MESSAGES_ALERT_TEMPLATE_DESC.format(**USERNAME_IN_BLACKLIST)
            # If username exists in Django users
            elif get_user_model().objects.filter(username=new_username):
                _err_msg = settings.MESSAGES_ALERT_TEMPLATE_DESC.format(**USERNAME_IN_BLACKLIST)
            if _err_msg:
                messages.add_message(request, messages.ERROR, _err_msg)
                return redirect('provisioning:change_username')

            # create token
            current_data = {'uid': lu.uid}
            new_data = {'uid': form.cleaned_data['new_username']}
            data = dict(ldap_dn = lu.dn,
                        is_active = True,
                        current_data = json.dumps(current_data),
                        new_data = json.dumps(new_data))
            data_check = {k:v for k,v in data.items()}
            id_change_conf = IdentityLdapChangeConfirmation.objects.filter(**data_check).first()
            if not id_change_conf or not id_change_conf.token_valid():
                id_change_conf = IdentityLdapChangeConfirmation.objects.create(**data)
                # send_email here. Only on creation
                id_change_conf.send_email(ldap_user=lu,
                                          lang=request.LANGUAGE_CODE)
            messages.add_message(request, messages.SUCCESS,
                                 settings.MESSAGES_ALERT_TEMPLATE_DESC.format(**CONFIRMATION_EMAIL))
            return redirect('provisioning:dashboard')
        for k,v in get_labeled_errors(form).items():
            messages.add_message(request, messages.ERROR,
                                 "<b>{}</b>: {}".format(k, strip_tags(v)))
        return redirect('provisioning:change_username')


def send_email_password_changed(lu, request):
    smd = {'hostname': settings.HOSTNAME,
           'reset_url': reverse('provisioning:reset_password_ask'),
           'password_expiration': lu.schacExpiryDate,
           'user': lu.uid}

    msg_subj = translate_to(_('Password changed'),
                            lang=request.LANGUAGE_CODE)
    msg_obj =  translate_to(settings.IDENTITY_PASSWORD_SUCCESFULL_CHANGED,
                            lang=request.LANGUAGE_CODE)
    mail_sent = send_mail(msg_subj,
                          msg_obj.format(**smd),
                          settings.DEFAULT_FROM_EMAIL,
                          lu.mail, # it's a list :)
                          fail_silently=True,
                          auth_user=None,
                          auth_password=None,
                          connection=None,
                          html_message=None)
    if mail_sent:
        mail_status = 'OK'
    else:
        mail_status = 'FAILED'
    logger.info('{} mail sent status: '.format(lu.uid, mail_status))
    return mail_sent


@login_required
@require_http_methods(["POST"])
@valid_ldap_user
def change_password(request):
    lu = LdapAcademiaUser.objects.filter(dn=request.user.dn).first()
    form = PasswordChangeForm(request.POST)

    delivery_dict = get_ldapuser_attrs_from_formbuilder_conf(lu)

    dyn_form = SavedFormContent.compiled_form(data_source=json.dumps(delivery_dict),
                                              constructor_dict=settings.DJANGO_FORM_BUILDER_FIELDS,
                                              ignore_format_field_name=True)

    d = {'form_delivery': dyn_form,
         'form_password': form,
         'lu': lu,
         'attrs': get_ldapuser_aai_html_attrs(lu)}

    if not form.is_valid():
        for k,v in get_labeled_errors(form).items():
            messages.add_message(request, messages.ERROR,
                                 "<b>{}</b>: {}".format(k, strip_tags(v)))
        return redirect('provisioning:dashboard')
    if lu.check_pwdHistory(form.cleaned_data['password']):
        messages.add_message(request, messages.ERROR,
                             settings.MESSAGES_ALERT_TEMPLATE_DESC.format(**PASSWORD_ALREADYUSED))
        return redirect('provisioning:dashboard')
    try:
        lu.set_password(password = form.cleaned_data['password'],
                        old_password = form.cleaned_data['old_password'])
    except Exception as e:
        return render(request,
                      'custom_message.html',
                      INVALID_DATA_DISPLAY, status=403)
    lu.set_default_schacExpiryDate()
    send_email_password_changed(lu, request)
    messages.add_message(request, messages.SUCCESS,
                         settings.MESSAGES_ALERT_TEMPLATE.format(**PASSWORD_CHANGED))
    return redirect('provisioning:dashboard')


def reset_password_ask(request):
    if request.method == 'GET':
        d = {'login_form': IdentityLoginForm(),
             'password_reset_form' : PasswordAskResetForm()}
        return render(request, 'password_reset_page.html', d)

    # we do not check if data are valid to avoid any vulnerability reconnaissance
    form = IdentityTokenAskForm(request.POST)
    if not form.is_valid():
        return render(request,
                      'custom_message.html',
                      INVALID_DATA_DISPLAY, status=403)
    username = form.cleaned_data['username']
    mail = form.cleaned_data['mail']
    schacPersonalUniqueID = '{}:{}'.format(settings.SCHAC_PERSONALUNIQUEID_DEFAULT_PREFIX_COMPLETE,
                                           form.cleaned_data['tin'].upper())
    if username:
        lu = LdapAcademiaUser.objects.filter(uid=username,
                                             mail__contains=mail).first()
    else:
        lu = LdapAcademiaUser.objects.filter(schacPersonalUniqueID__contains=schacPersonalUniqueID,
                                             mail__contains=mail).first()
    # is user exists run the game
    if lu:
        if not lu.is_renewable():
            return render(request,
                          'custom_message.html',
                          IDENTITY_DISABLED, status=403)
        # try to reuse existing ones...
        id_pwd_reset = IdentityLdapPasswordReset.objects.filter(ldap_dn=lu.dn,
                                                                is_active=True,
                                                                valid_until__gt=timezone.localtime()).last()
        # otherwise create a brand new one
        if not id_pwd_reset:
            data = dict(ldap_dn=lu.dn,
                        is_active=True)
            id_pwd_reset = IdentityLdapPasswordReset.objects.create(**data)
        # send email and update token status
        id_pwd_reset.send_email(ldap_user=lu,
                                lang=request.LANGUAGE_CODE)
        logger.info('Password Reset Ask for {}'.format(lu.uid))
    messages.add_message(request, messages.SUCCESS,
                         settings.MESSAGES_ALERT_TEMPLATE_DESC.format(**PASSWORD_ASK_RESET))
    return redirect('provisioning:home')


def reset_password_token(request, token_value):
    # check if the token is valid
    id_prov = get_object_or_404(IdentityLdapPasswordReset,
                                token=token_value)
    if not id_prov.token_valid():
        return render(request,
                      'custom_message.html',
                      INVALID_TOKEN_DISPLAY, status=403)
    if request.method == 'GET':
        return render(request,
                      'password_reset_token.html',
                      {'form': PasswordResetForm(),
                       'token_value': token_value})
    elif request.method == 'POST':
        # check if form is valid
        form = PasswordResetForm(request.POST)
        if not form.is_valid():
            return render(request,
                          'password_reset_token.html',
                          {'form': form,
                           'token_value': token_value})
        # check se i dati immessi corrispondono
        username = form.cleaned_data['username']
        mail = form.cleaned_data['mail']
        lu = LdapAcademiaUser.objects.filter(uid=username,
                                             mail__contains=mail).first()
        if lu and not lu.is_renewable():
            return render(request,
                          'custom_message.html',
                          IDENTITY_DISABLED, status=403)
        if not lu or lu.dn != id_prov.ldap_dn:
            return render(request,
                          'custom_message.html',
                          PASSWORD_SUBMISSION_NOT_VALID,
                          status=403)
        if lu and lu.check_pwdHistory(form.cleaned_data['password']):
            return render(request,
                          'custom_message.html',
                          PASSWORD_ALREADYUSED)
        try:
            lu.set_password(password = form.cleaned_data['password'])
        except Exception as e:
            return render(request,
                          'custom_message.html',
                          INVALID_DATA_DISPLAY, status=403)
        send_email_password_changed(lu, request)
        id_prov.mark_as_used()
        lu.enable()
        lu.set_default_schacExpiryDate()
        logger.info('{} changed his Password with a Token'.format(lu.uid))

        return render(request,
                      'custom_message.html',
                      PASSWORD_CHANGED)
    else:
        return render(request,
                      'custom_message.html',
                      INVALID_ACCESS_DISPLAY, status=403)
