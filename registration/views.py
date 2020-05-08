import base64
import json
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django_form_builder.enc import encrypt, decrypt
from django_form_builder.forms import BaseDynamicForm
from django_form_builder.models import DynamicFieldMap


from . forms import AskForm_1

logger = logging.getLogger(__name__)


def ask(request):
    if request.method == 'GET':
        form_captcha = DynamicFieldMap.get_form(BaseDynamicForm,
                                                constructor_dict=settings.REGISTRATION_CAPTCHA_FORM)

        d = dict(form = AskForm_1(),
                 form_captcha = form_captcha)

        return render(request, 'ask.html', d)
    else:
        form = AskForm_1(request.POST)
        form_captcha = DynamicFieldMap.get_form(BaseDynamicForm,
                                                constructor_dict=settings.REGISTRATION_CAPTCHA_FORM,
                                                data = request.POST)

        if not (form.is_valid() and form_captcha.is_valid()):
            logger.error('Registration form is not valid: {}'.format(json.dumps(form.cleaned_data)))
            return render(request, 'ask.html', {'form': form,
                                                'form_captcha': form_captcha})
        # it seems quite good, check its delivery address
        token = base64.b64encode(encrypt(json.dumps(form.cleaned_data)))
        _msg = _('{} {} [{}] have requested to be registered as a new user.')
        logger.info(_msg.format(form.cleaned_data['name'],
                                form.cleaned_data['surname'],
                                form.cleaned_data['mail'],))
        request_path = reverse('registration:confirm', kwargs={'token': token.decode()})
        _offset = request.build_absolute_uri().index('/', 7)
        request_fqdn = '{}{}'.format(request.build_absolute_uri()[:_offset],
                                     request_path)

        mail_body = dict(name = '{} {}'.format(form.cleaned_data['name'],
                                               form.cleaned_data['surname']),
                         url = request_fqdn)
        
        mail_sent = send_mail(settings.REGISTRATION_ASK_OBJ,
                              settings.REGISTRATION_ASK_BODY.format(**mail_body),
                              settings.DEFAULT_FROM_EMAIL,
                              [form.cleaned_data['mail']], # it's a list :)
                              fail_silently=True)
        if not mail_sent:
            logger.error('Email to {} cannot be send.'.format(cleaned_data['mail']))
            
            return render(request,
                          'custom_message.html',
                          dict(title = _('EMail send error'),
                               avviso = _('It have been occurred an Error sending the confirmation email to you'),
                               description = _('Please try later.')), status=403)
        else:
            return HttpResponseRedirect(reverse('unical_template:confirmation-email'))

def confirm(request, token):
    if request.method == 'GET':
        data = json.loads(decrypt(token).decode())
        import pdb; pdb.set_trace()      
        # check collissions
        # email, cf
            
        # if true redirect to an informational page
    else:
        import pdb; pdb.set_trace()
    pass
