from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from eservice.models import EService

from eservice.models import EServiceType

from system.settings import base


class ClientApi(models.Model):
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    first_name = models.CharField(verbose_name='Імя', max_length=30)
    last_name = models.CharField(verbose_name='Прізвище', max_length=30)
    middle_name = models.CharField(max_length=64, verbose_name='По батькові')
    password_api = models.CharField(verbose_name='Пароль', max_length=128)
    login_api = models.CharField(verbose_name='Логін', max_length=128)

    ip_or_domain = models.CharField(max_length=64, verbose_name='Особистий телефон')

    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))

    # @receiver(post_save, sender=base.AUTH_CLIENT_MODEL)
    # def create_auth_token(sender, instance=None, created=False, **kwargs):
    #     if created:
    #         Token.objects.create(user_id=instance.id)

    class Meta:
        verbose_name = 'Клієнти'
        verbose_name_plural = 'Клієнти'

    def __str__(self):
        return self.last_name + ' ' + self.first_name


class ClientApiEService(models.Model):
    client = models.ForeignKey(ClientApi, null=True, verbose_name="Клієнт", on_delete=models.CASCADE, )
    eservice = models.ForeignKey(EServiceType, null=True, verbose_name="Послуга", on_delete=models.CASCADE, )

    class Meta:
        verbose_name = 'Клієнти_Послуги'
        verbose_name_plural = 'Клієнти_Послуги'
        unique_together = (("client", "eservice"),)

    def __str__(self):
        return self.client.first_name + ' ' + self.eservice.title


class ClientApiEServiceField(models.Model):
    client_api_eservice = models.ForeignKey(ClientApiEService, null=True, verbose_name="Клієнт",
                                            on_delete=models.CASCADE, )
    field = models.CharField(max_length=64, verbose_name='Поле')

    def __str__(self):
        return self.client_api_eservice.client.first_name
