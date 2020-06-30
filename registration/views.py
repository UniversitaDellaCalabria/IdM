import copy
import datetime
import json
import logging

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django_form_builder.enc import encrypt, decrypt
from django_form_builder.forms import BaseDynamicForm

from identity.models import Identity
from ldap_peoples.models import LdapAcademiaUser
from provisioning.models import create_activation_token

from . forms import AskForm_1, IdentityDocumentForm
from . utils import (validate_personal_id,
                     serialize_dict,
                     create_registration_token,
                     build_registration_token_url)


logger = logging.getLogger(__name__)


LDAP_UNIQUEID_TMPL = getattr(settings, 'LDAP_UNIQUEID_TMPL',
                             'urn:schac:personalUniqueID:it:CF:{}')


def ask(request):
    cdict = copy.copy(settings.REGISTRATION_CAPTCHA_FORM)

    if request.method == 'GET':
        form_captcha = BaseDynamicForm.get_form(constructor_dict=cdict,
                                                custom_params={'lang': translation.get_language()})
        d = dict(form = AskForm_1(),
                 form_captcha = form_captcha)

        return render(request, 'ask.html', d)
    else:
        form = AskForm_1(request.POST)
        form_captcha = BaseDynamicForm.get_form(constructor_dict=cdict,
                                                data = request.POST)

        if not (form.is_valid() and form_captcha.is_valid()):
            dform = str(dict(form.cleaned_data))
            logger.error('Registration form is not valid: {}'.format(dform))
            return render(request, 'ask.html', {'form': form,
                                                'form_captcha': form_captcha})
        # validate tin
        if not validate_personal_id(form.cleaned_data['tin']):
            logger.error('Registration form is not valid, tin validation failed: {}'\
                          .format(form.cleaned_data['tin']))
            return render(request,
                          'custom_message.html',
                          dict(title = _('TIN code validation failed'),
                               avviso = _('It have been occurred an error validating your TIN'),
                               description = ''), status=403)

        # it seems quite good, check its delivery address
        serialized_dict = serialize_dict(form.cleaned_data)

        token = create_registration_token(serialized_dict)
        _msg = _('{} {} [{}] [{}] have requested to be registered as a new user.')
        logger.info(_msg.format(form.cleaned_data['name'],
                                form.cleaned_data['surname'],
                                form.cleaned_data['mail'],
                                form.cleaned_data['tin']))
        request_fqdn = build_registration_token_url(request, token)

        mail_body = dict(name = '{} {}'.format(form.cleaned_data['name'],
                                               form.cleaned_data['surname']),
                         url = request_fqdn)

        mail_sent = send_mail(settings.REGISTRATION_ASK_OBJ,
                              settings.REGISTRATION_ASK_BODY.format(**mail_body),
                              settings.DEFAULT_FROM_EMAIL,
                              [form.cleaned_data['mail']], # it's a list :)
                              fail_silently=True)
        if not mail_sent:
            logger.error('Email to {} cannot be send.'.format(form.cleaned_data['mail']))

            return render(request,
                          'custom_message.html',
                          dict(title = _('Email send error'),
                               avviso = _('It have been occurred an Error '
                                          'sending the confirmation email to you'),
                               description = _('Please try later.')), status=403)
        else:
            return HttpResponseRedirect(reverse('unical_template:confirmation-email'))


def confirm(request, token):
    data = {}
    try:
        data = json.loads(decrypt(token).decode())
    except Exception as e:
        logger.error('Registration request Token encryption error')
        _msg = {'title': _("Invalid Token"),
               'avviso': _("Invalid data submission"),
               'description': ''}
        return render(request, 'custom_message.html',
                      _msg, status=403)

    form = AskForm_1(data)
    for k in form.fields:
        form.fields[k].widget.attrs['readonly'] = True
        form.fields[k].widget.attrs['disabled'] = True

    # check if identity was already created, if yes drive the user to the provisioning token
    identity = Identity.objects.filter(Q(tin__iexact=data['tin'])|\
                                       Q(mail__iexact=data['mail']))

    # TEST RDBMS REGISTRATION IDENTITY
    _msg = ', '.join(('{}:{}'.format(k,v) for k,v in data.items()))
    if identity:
        logger.error('Registration: IDENTITY already exists {}'.format(_msg))
        _msg = {'title': _("Invalid Registration"),
                'avviso': _("It seems that your email or your identification code already exists"),
                'description': _('Please go in the Home Page and activate '
                                 'the "Forgot your Password" procedure. '
                                 'If the problem persists please contact our technical assistance.')}
        return render(request, 'custom_message.html', _msg, status=403)

    # TEST LDAP
    tin = LDAP_UNIQUEID_TMPL.format(data['tin'])
    spltd_tin = tin.split(':')
    tin2 = ':'.join((spltd_tin[0], spltd_tin[1], spltd_tin[2],
                      spltd_tin[3].upper(), spltd_tin[4].upper(),
                      spltd_tin[5]))
    lu = LdapAcademiaUser.objects.filter(Q(schacPersonalUniqueID=tin)|\
                                         Q(schacPersonalUniqueID=tin2)|\
                                         Q(mail=data['mail']))
    if lu:
        logger.error('Registration: LDAP ACCOUNT - user already exists {}'.format(_msg))
        _msg = {'title': _("Invalid Data"),
                'avviso': _("It seems that you are already registered"),
                'description': _('Please go in the Home Page and activate '
                                'the "Forgot your Password" procedure')}
        return render(request, 'custom_message.html', _msg, status=403)


    if request.method == 'GET':
        # build the form with initial data plus document fron and retro fiel field
        context = dict(form = form,
                       form_document = IdentityDocumentForm())
        return render(request, 'confirm.html', context)

    if request.method == 'POST':
        form_document = IdentityDocumentForm(request.POST,
                                             request.FILES)
        # validate the form
        if not form_document.is_valid():
            context = dict(form = form,
                           form_document = form_document)
            return render(request, 'confirm.html', context)

        # create the identity
        data['document_front'] = form_document.cleaned_data['document_front']
        data['document_retro'] = form_document.cleaned_data['document_retro']
        data.pop('_dyn', '')
        data.pop('_hidden_dyn', '')
        # create an identity
        identity = Identity.objects.create(**data)
        # the redirect to password reset
        id_prov = create_activation_token(identity)
        return HttpResponseRedirect(id_prov.get_activation_url())


@staff_member_required
def get_registration_token(request):
    """
    urllib.parse.urlencode(dictionary)
    """
    form = AskForm_1(request.GET)
    if form.is_valid():
        token = create_registration_token(form.cleaned_data)
        request_fqdn = build_registration_token_url(request, token)
        return HttpResponse(request_fqdn)
    else:
        return JsonResponse(form.errors, status=403)
