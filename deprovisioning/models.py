from django.db import models
from django.utils.translation import gettext as _


class AccountUpdateLog(models.Model):
    uid = models.CharField(_('Account id'), max_length=135)
    event = models.CharField(_('Event'), max_length=150, blank=True, null=True)
    backup = models.TextField(_('Json attributes'), blank=False, null=False)
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        verbose_name_plural = _("Account update logs")

    def __str__(self):
        return '{} {}'.format(self.uid, self.event)
