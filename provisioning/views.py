import json

from collections import OrderedDict
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import (HttpResponse,
                         Http404,
                         HttpResponseForbidden,
                         HttpResponseRedirect,
                         HttpResponseNotFound)
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from . custom_messages import *
from . decorators import *
from . forms import *
from . models import *
from . utils import translate_to

from ldap_peoples.models import LdapAcademiaUser


def account_create(request, token_value):
    id_prov = get_object_or_404(IdentityProvisioning, token=token_value)
    if not id_prov.token_valid():
        return render(request,
                      'custom_message.html',
                      INVALID_TOKEN_DISPLAY,
                      status=403)
    d = {'APP_NAME': settings.APP_NAME}

    if request.method == 'GET':
        form = AccountCreationForm(initial={'token': token_value})
        d['form'] = form
        return render(request, 'account_create.html', d)
    elif request.method == 'POST':
        data = request.POST.copy()
        data['token'] = token_value
        form = AccountCreationForm(data)
        d['form'] = form

        if not form.is_valid():
            return render(request, 'account_create.html', d)

        if data['token'] != id_prov.token or \
           data['mail'] != id_prov.identity.email:
               return render(request,
                             'custom_message.html',
                             INVALID_DATA_DISPLAY, status=403)

        # TODO, gestire title (multivalued) LDAP qui!
        entry = {'uid' : form.cleaned_data['username'],
                 'cn' : id_prov.identity.name,
                 'givenName' : id_prov.identity.name,
                 'sn' : id_prov.identity.surname,
                 'displayName' : ' '.join((id_prov.identity.name,
                                           id_prov.identity.surname)),
                 'mail' : [form.cleaned_data['mail']],
                 'telephoneNumber' : [id_prov.identity.telephone,],
                 'schacPlaceOfBirth' : ','.join((id_prov.identity.nation,
                                                 id_prov.identity.place_of_birth)),
                 'schacDateOfBirth' : id_prov.identity.date_of_birth,
                 'schacHomeOrganization' : settings.SCHAC_HOMEORGANIZATION_DEFAULT}

        ldap_user = LdapAcademiaUser.objects.create(**entry)
        #ldap_user.userPassword = form.cleaned_data['password']
        # ldap_user.set_password_custom(form.cleaned_data['password'])
        ldap_user.set_schacPersonalUniqueID(value=id_prov.identity.fiscal_code,
                                            country_code=id_prov.identity.nation)
        ldap_user.set_default_eppn()
        for homeorgtype in settings.SCHAC_HOMEORGANIZATIONTYPE_DEFAULT:
            ldap_user.set_schacHomeOrganizationType(value=homeorgtype)

        # AFFILIATIONS
        affiliations = id_prov.identity.affiliation.split(',')
        ldap_user.eduPersonAffiliation = id_prov.identity.affiliation.split(',')
        eduPersonScopedAffiliation = [aff+'@'+settings.LDAP_BASE_DOMAIN for aff in affiliations]
        # additionals

        # additionals affiliations
        addaff = id_prov.identity.additionalaffiliation_set.all()
        additional_affiliations = [aff.get_scoped() for aff in addaff]
        eduPersonScopedAffiliation.extend(additional_affiliations)
        ldap_user.eduPersonScopedAffiliation = eduPersonScopedAffiliation

        # additional personal unique codes from additionals affiliations
        ldap_user.schacPersonalUniqueCode = [aff.get_urn() for aff in addaff]
        ldap_user.save()

        # altrimenti mi fallisce lo unit test!
        ldap_user.set_password(form.cleaned_data['password'])

        id_prov.mark_as_used()
        id_prov.identity.activation_date = timezone.localtime()
        id_prov.identity.save()
        return render(request,
                      'custom_message.html',
                      ACCOUNT_SUCCESFULLY_CREATED)

def home(request):
    """render the home page"""
    if request.user.is_authenticated:
        # return HttpResponseRedirect(reverse(settings.LOGIN_REDIRECT_URL))
        return HttpResponseRedirect(reverse('provisioning:dashboard'))
    # peers = AllowedImportPeer.objects.all()
    d = {'login_form': IdentityLoginForm(),
         'password_reset_form' : PasswordAskResetForm()}
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
            # aggiungi form errors qui + messages
            return render(request,
                          'custom_message.html',
                          INVALID_ACCESS_DISPLAY, status=403)
        username = login_form.cleaned_data['username']
        password = login_form.cleaned_data['password']
        user = authenticate(username=username,
                            password=password)
        if user:
            login(request, user)
            if request.POST.get('next'):
                return HttpResponseRedirect(request.POST.get('next'))
            return HttpResponseRedirect(reverse('provisioning:dashboard'))
        else:
            # aggiungi form errors qui + messages
            return render(request,
                          'custom_message.html',
                          ACCOUNT_NOT_EXISTENT,
                           status=403)
    else:
        # login form if method == 'GET'
        d = {'login_form': IdentityLoginForm()}
        return render(request,
                      'provisioning_login.html', d)


def get_ldapuser_aai_html_attrs(lu):
    hidden_attributes = ['userPassword',
                         'sambaNTPassword',
                         'creatorsName',
                         'modifiersName',
                         'pwdHistory']
    attributes = OrderedDict()
    for k in sorted(lu.__dict__.keys()):
        if k[0] == '_' or k in hidden_attributes: continue
        attributes[k] = lu.__dict__[k]
    for k,v in attributes.items():
        if isinstance(v, list):
            attributes[k] = '<br>'.join(v)
    return attributes

@login_required
def dashboard(request):
    d = {}
    if request.user.dn:
        lu = LdapAcademiaUser.objects.filter(dn=request.user.dn).first()
        if not lu:
            return render(request,
                          'custom_message.html',
                          USER_DEFINITION_ERROR,
                           status=403)
        delivery_dict = {'mail': lu.mail[0]}
        if lu.telephoneNumber:
            delivery_dict['telephoneNumber'] = lu.telephoneNumber[0]
        d = {'form_delivery': DeliveryForm(initial=delivery_dict),
             'form_password': PasswordChangeForm(),
             'form_profile': ProfileForm(initial={'access_notification': \
                                                  request.user.access_notification}),
             'lu': lu,
             'attrs': get_ldapuser_aai_html_attrs(lu)}
    return render(request, 'dashboard.html', d)

@login_required
@valid_ldap_user
def change_deliveries(request, token_value=None):
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
        lu.save()
        id_prov.mark_as_used()

        return render(request,
                      'custom_message.html',
                      DATA_CHANGED)

    elif request.method == 'POST':
        form = DeliveryForm(request.POST)
        d = {'form_delivery': form,
             'form_password': PasswordForm(),
             'form_profile': ProfileForm(initial={'access_notification': \
                                                  request.user.access_notification}),
             'lu': lu,
             'attrs': get_ldapuser_aai_html_attrs(lu)}

        if not form.is_valid():
            return render(request, 'dashboard.html', d)

        # create token
        current_data = {}
        new_data = {k:v for k,v in form.cleaned_data.items()}
        for k in form.cleaned_data:
            attr = getattr(lu, k)
            if isinstance(attr, list):
                current_data[k] = attr[-1] if attr else []
            else:
                current_data[k] = attr

        # profile options
        form_profile = ProfileForm(request.POST)
        if not form_profile.is_valid():
            return render(request, 'dashboard.html', d)

        access_notification = form_profile.cleaned_data.get('access_notification')
        if request.user.access_notification != access_notification:
            new_data['access_notification'] = access_notification
            current_data['email_access_notifications'] = request.user.access_notification

        # data was not changed
        if current_data == new_data or not new_data:
            return HttpResponseRedirect(reverse('provisioning:dashboard'))

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
        return render(request,
                      'custom_message.html',
                      CONFIRMATION_EMAIL)
    else:
        return render(request,
                      'custom_message.html',
                      INVALID_DATA_DISPLAY, status=403)

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
    return mail_sent

@login_required
@require_http_methods(["POST"])
@valid_ldap_user
def change_password(request):
    lu = LdapAcademiaUser.objects.filter(dn=request.user.dn).first()
    form = PasswordChangeForm(request.POST)
    d = {'form_delivery': DeliveryForm(initial={'mail': lu.mail[0]}),
         'form_password': form,
         'lu': lu,
         'attrs': get_ldapuser_aai_html_attrs(lu)}

    if lu.telephoneNumber:
        d['telephoneNumber'] = lu.telephoneNumber[0]

    if not form.is_valid():
        return render(request, 'dashboard.html', d)
    if lu.check_pwdHistory(form.cleaned_data['password']):
        return render(request,
                      'custom_message.html',
                      PASSWORD_ALREADYUSED)
    try:
        lu.set_password(password = form.cleaned_data['password'],
                        old_password = form.cleaned_data['old_password'])
    except Exception as e:
        return render(request,
                      'custom_message.html',
                      INVALID_DATA_DISPLAY, status=403)
    lu.reset_schacExpiryDate()
    send_email_password_changed(lu, request)
    return render(request,
                  'custom_message.html',
                  PASSWORD_CHANGED)

@require_http_methods(["POST"])
def reset_password_ask(request):
    # we do not check if data are valid to avoid any vulnerability reconnaissance
    form = IdentityTokenAskForm(request.POST)
    if not form.is_valid():
        print(form.errors)
        return render(request,
                      'custom_message.html',
                      INVALID_DATA_DISPLAY, status=403)
    username = request.POST.get('username')
    mail = request.POST['mail']
    if username:
        lu = LdapAcademiaUser.objects.filter(uid=username,
                                             mail__icontains=mail).first()
    else:
        lu = LdapAcademiaUser.objects.filter(mail__icontains=mail).first()
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
    return render(request,
                  'custom_message.html',
                  PASSWORD_ASK_RESET)

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
                                             mail__icontains=mail).first()
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
        lu.reset_schacExpiryDate()
        return render(request,
                      'custom_message.html',
                      PASSWORD_CHANGED)
    else:
        return render(request,
                      'custom_message.html',
                      INVALID_ACCESS_DISPLAY, status=403)
