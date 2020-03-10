# -*- coding: utf-8 -*-

from django.db import models
from model_utils.models import TimeStampedModel, SoftDeletableModel
from django.conf import settings
from django.template.defaultfilters import date as dj_date
from django.utils.translation import ugettext as _
from django.utils.timezone import localtime


class Dialog(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Dialog owner"), related_name="selfDialogs",
                              on_delete=models.CASCADE)
    opponent = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Dialog opponent"), on_delete=models.CASCADE, null=True)

    def __str__(self):
        return _("Chat with ") + self.owner.username

    class Meta:
        verbose_name = 'Діалог'
        verbose_name_plural = 'Діалоги'


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    if instance.sender.is_operator():
        return 'support/operators/user_{0}/{1}'.format(instance.sender.id, filename)
    else:
        return 'support/users/user_{0}/{1}'.format(instance.sender.id, filename)


class Message(TimeStampedModel, SoftDeletableModel):
    dialog = models.ForeignKey(Dialog, verbose_name=_("Dialog"), related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Author"), related_name="messages",
                               on_delete=models.CASCADE)
    text = models.TextField(verbose_name=_("Message text"))
    read = models.BooleanField(verbose_name=_("Read"), default=False)
    file = models.FileField(verbose_name=_("File"), upload_to=user_directory_path, null=True, blank=True)
    filename = models.CharField(max_length=200, verbose_name=_("Filename"), null=True, blank=True)
    all_objects = models.Manager()

    def get_formatted_create_datetime(self):
        return dj_date(localtime(self.created), settings.DATETIME_FORMAT)

    def __str__(self):
        return self.sender.username + "(" + self.get_formatted_create_datetime() + ") - '" + self.text + "'"

    class Meta:
        ordering = ['created']
        verbose_name = 'Повідомлення'
        verbose_name_plural = 'Повідомлення'
