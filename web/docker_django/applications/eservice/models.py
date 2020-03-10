import os
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.db.models import QuerySet
from django_extensions.db.fields.json import JSONField
from django.contrib.auth import get_user_model
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

User = get_user_model()


def validate_capitalized(value):
    if value[0] != value[0].capitalize():
        raise ValidationError('Введіть будь ласка назву з великої літери: %(value)s',
                              code='invalid',
                              params={'value': value})


def file_extension(value):
    import os
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx', '.odt', '.rtf', '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.xls',
                        '.xlsx']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Недоступне розширення файлу')


class HideOldVersion(models.Manager):
    def get_queryset(self):
        return super(HideOldVersion, self).get_queryset().filter(is_archival=False)


class EService(models.Model):
    internal_id = models.CharField(max_length=128, unique=True, null=False, blank=False,
                                   verbose_name='Індекс реєстрації послуги')
    created_at = models.DateTimeField(default=datetime.now, verbose_name="Створено")
    title = models.CharField(max_length=512, blank=False, null=False, verbose_name='Короткий опис',
                             validators=[validate_capitalized])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, verbose_name="Автор картки",
                                   on_delete=models.CASCADE)
    created_by_ip = models.CharField(default='127.0.0.1', max_length=15, verbose_name='IP адреса автора картки')
    deadline = models.DateField(null=True, verbose_name='Кінечний строк')
    close_at = models.DateTimeField(null=True, verbose_name="Послугу завершенно")
    type = models.ForeignKey('EServiceType', default=1, verbose_name='Тип послуги', on_delete=models.SET_DEFAULT)
    version = models.IntegerField(null=False, default="1", verbose_name='Версія послуги')
    period_extended = models.DateTimeField(null=True, blank=True, verbose_name="Дата продовження послуги")
    resolutioner = models.ForeignKey(User, null=True, verbose_name="Накладає резолюцію", on_delete=models.SET_NULL,
                                     related_name="resolutioner")
    status = models.ForeignKey('EServiceMeta', null=True, verbose_name="Стан послуги", default=6,
                               on_delete=models.SET_DEFAULT)
    resolutioner_viewed = models.BooleanField(default=False, verbose_name="Переглянуто резолюцілнером")
    edit_comment = models.CharField(max_length=1024, null=True, verbose_name="Коментар відправившого на доопрацювання")
    # TODO: реалізувати безпечне видалення
    is_deleted = models.CharField(max_length=10, null=True, verbose_name='Видалено?', default=False)

    # Показуємо тільки
    # objects = HideOldVersion()
    # all = models.Manager()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'eservice'
        verbose_name = 'Послуги'
        verbose_name_plural = 'Послуги'
        unique_together = ["internal_id", "id"]
        select_on_save = True


# types of document
class EServiceType(models.Model):
    title = models.CharField(max_length=128)
    category = models.CharField(max_length=128, default='Вхідна кореспонденція')
    controller = models.CharField(max_length=128, default='dev')
    model = models.CharField(max_length=128, default='EService')

    class Meta:
        db_table = 'eservice_type'
        verbose_name = 'Тип послуги'
        verbose_name_plural = 'Типи послуги'

    def __str__(self):
        return self.title


class EServiceStatus(models.Model):
    '''
    Статуси для типів послуги
    '''
    title = models.CharField(max_length=160, default='Чернетка')
    slug = models.CharField(max_length=60, default='draft')
    color = models.CharField(max_length=60, default='text-default')

    class Meta:
        db_table = 'eservice_status'
        verbose_name = 'Статус послуги'
        verbose_name_plural = 'Статуси послуги'
        unique_together = ('title', 'slug',)

    def __str__(self):
        return self.title


# Файли тримаємо у папках з іменами ID відповідних послуг
def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "{}__{}__{:%d-%m-%Y}__ID-{}.{}".format(
        instance.eservice.type.title,
        instance.eservice.internal_id.replace("/","."),
        instance.eservice.created_at,
        instance.eservice.id, ext)
    return 'eservice_files/{0}/{1}'.format(instance.eservice.id, filename)


class EServiceFile(models.Model):
    """
    Збереження файлів для послуги.
    """
    created_at = models.DateTimeField(default=datetime.now)
    eservice = models.ForeignKey(EService, verbose_name="Послугу", null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path, blank=False, null=False, validators=[file_extension])
    filename = models.CharField(max_length=128, null=False, default="Custom name")
    mime = models.CharField(max_length=150, default="image/jpeg", verbose_name="Тип файлу")
    size = models.IntegerField(null=True, verbose_name="Розмір файлу")

    class Meta:
        db_table = 'eservice_file'
        verbose_name = 'Файл'
        verbose_name_plural = 'Файли'


class EServiceSign(models.Model):
    """

    """
    created_at = models.DateTimeField(default=datetime.now)
    eservice = models.ForeignKey(EService, verbose_name="Послугу", null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'eservice_sign'
        verbose_name = 'Підпис файлу'
        verbose_name_plural = 'Підпис файлу'
        unique_together = (('eservice', 'user'),)


# Логування усіх дій по послуги
class EServiceLog(models.Model):
    activity = models.CharField(max_length=512, blank=True)
    eservice = models.ForeignKey(EService, null=False, blank=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'eservice_log'
        verbose_name = 'Лог подій по послуги'
        verbose_name_plural = 'Логі подій по послуги'


class EServiceStar(models.Model):
    eservice = models.ForeignKey(EService, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, null=True, on_delete=models.CASCADE)
    quality = models.FloatField(null=True, blank=True, default=None)
    easy_ordering = models.FloatField(null=True, blank=True, default=None)
    term_service = models.FloatField(null=True, blank=True, default=None)
    average_value = models.FloatField(null=True, blank=True, default=None)
    comment = models.TextField(default='', blank=True, null=True)

    class Meta:
        db_table = 'eservice_star'
        verbose_name = 'Оцінюваня надання послуги'
        verbose_name_plural = 'Оцінюваня надання послуги'


class EServiceMeta(MPTTModel):
    eservice_type = models.ForeignKey(EServiceType, null=True, blank=True, on_delete=models.SET_NULL)
    category_index = models.CharField(max_length=10, null=False, verbose_name="Індекс категорії")
    title = models.CharField(max_length=1024, null=False, verbose_name="Назва")
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True,
                            verbose_name="Батьківська категорія", on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True, verbose_name="Активна?")
    is_category = models.BooleanField(default=False, verbose_name="Категорія?")

    created_at = models.DateTimeField(default=datetime.now)
    attr = JSONField(blank=True, null=True, verbose_name='Додаткова інформація')

    objects = QuerySet.as_manager()

    class MPTTMeta:
        order_insertion_by = ['category_index']

    class Meta:
        db_table = 'eservice_meta'
        verbose_name = 'Мета-інформація'
        verbose_name_plural = 'Мета-інформація'

    def __str__(self):
        return "{} ({})".format(self.title, self.category_index)


# =============== Допоміжні функції по роботі з моделями ==============#

class Log:
    '''
    Логування основних дій
    '''

    def __init__(self, **kwargs):
        self.eservice_id = kwargs['eservice_id']
        self.action = kwargs['action']
        self.user = kwargs['user']
        self.time = datetime.now()

    def write(self):
        try:
            EServiceLog.objects.create(
                eservice=EService.objects.get(pk=self.eservice_id),
                activity=self.action,
                created_by=self.user,
                created_at=self.time
            ).save()
        except Exception as e:
            return "Помилка запису логу події: {}".format(e)


# Погодження послуги
class EServiceOnApproving(models.Model):
    eservice = models.ForeignKey(EService, on_delete=models.CASCADE)
    assign_to = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="created_approver_item_by",
                                   on_delete=models.CASCADE)
    created_by_ip = models.CharField(default='127.0.0.1', max_length=15)
    done = models.IntegerField(default=0)
    done_at = models.DateTimeField(null=True)
    viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True)
    submitted = models.BooleanField(default=0)
    comment = models.TextField(default='', blank=True, null=True)

    class Meta:
        unique_together = ('eservice', 'assign_to')
        db_table = 'eservice_on_approving'


class GeoCity(models.Model):
    code = models.CharField(max_length=10)
    type = models.CharField(max_length=2, null=True)
    # prefix = models.CharField(max_length=5)
    name = models.CharField(verbose_name="Населений пункт", max_length=256)
    # specialized_name = models.CharField(max_length=256)
    # is_residential = models.BooleanField(default=False, verbose_name="Переглянуто резолюцілнером")
    # parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    parent = models.ForeignKey("self", on_delete=models.CASCADE,  db_column='parent', null=True, blank=True, related_name='children')

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        managed = False
        db_table = 'geo_city'
