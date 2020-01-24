from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail, mail_admins
from django.urls import reverse
from django.utils import timezone

from .models import *
