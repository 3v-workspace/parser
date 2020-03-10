from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
TEMPORARY_CODE_SIZE = 16


class Token(models.Model):
    """Модель аутентифікаційних даних користувача .
    """
    class Meta:
        db_table = 'auth_token'

    signature = models.CharField(max_length=64)
    cl_id = models.CharField(max_length=64, null=True, unique=True)
    cl_id_text = models.CharField(max_length=512, default='')
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='token',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    date_created = models.DateTimeField(auto_now_add=True)


class UserTemporaryCode(models.Model):
    """Модель для отримання користувача за тимчасовим ключем.
    Запис існує протягом реєстрації користувача.
    """
    class Meta:
        db_table = 'auth_user_temporary_code'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='user_code',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    code = models.CharField(max_length=TEMPORARY_CODE_SIZE, unique=True, null=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
