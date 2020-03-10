from datetime import datetime, timedelta

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager, Group
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db.models.signals import post_save
from django.db import models
from django.core.mail import send_mail
from django.core import validators
from django.dispatch import receiver
from django.contrib.auth.models import Group
from system.helpers import send_letter
from django.db.models import Q
from mptt.models import MPTTModel, TreeForeignKey
from support.models import Dialog, Message

from .managers import TemporalQuerySet
from .utils import get_dept_final_date


class Organization(models.Model):
    edrpou = models.CharField(max_length=100, verbose_name="Код ЄДРПОУ", blank=True, null=True)
    name = models.CharField(max_length=100, verbose_name="Назва організації", blank=True, null=True)
    date_creation = models.DateTimeField(_("date creation"), default=timezone.now)


class UserManagerCustom(BaseUserManager):
    def create_user(self, unique_code, password=None,
                    is_superuser=False, is_staff=False,
                    is_active=True):

        user = self.model()
        now = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")

        from random import randint
        range_start = 10 ** (10 - 1)
        range_end = (10 ** 10) - 1

        user.unique_code = str(randint(range_start, range_end))+str(now)
        user.set_password(password)  # change password to hash
        user.staff = is_staff
        user.active = is_active
        user.is_superuser = is_superuser
        user.save(using=self._db)
        return user

    def create_superuser(self, unique_code, password=None,):
        user = self.create_user(
            unique_code,
            password=password,
            is_staff=True,
            is_superuser=True,
        )
        return user


class User(AbstractBaseUser, PermissionsMixin):
    TYPE_USER = (
        ("physical", "physical"), #фізична особа
        ("legal", "legal"), #представник юридичної особи
        ("fop", "fop"), # фізична особа-підприємець
    )
    email = models.EmailField(
        _("email address"),
        unique=False,
        blank=True, null=True,
        error_messages={
            "unique": "Користувач з такою електронною поштою вже існує",
        })

    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    first_name = models.CharField(_("first name"), max_length=30)
    last_name = models.CharField(_("last name"), max_length=30)
    middle_name = models.CharField(max_length=64, verbose_name="по батькові")

    phone = models.CharField(max_length=64, verbose_name="Особистий телефон")
    birthday = models.DateField(null=True, blank=True, verbose_name="День народження")
    passport = models.CharField(max_length=64, verbose_name="Паспортні дані")
    auth_type = models.CharField(max_length=64, null=True, blank=True, verbose_name="Тип логінізації", default="dig_sign")
    identification_code = models.CharField(max_length=100, verbose_name="Ідинтифікаційний код", default="0")
    # system field
    username = models.CharField(
        _("username"),
        max_length=30,
        help_text=_("Required. 30 characters or fewer. "
                    "Letters, digits and @/./+/-/_ only."),
        validators=[
            validators.RegexValidator(
                r"^[\w.@+-]+$",
                _("Enter a valid username. "
                "This value may contain only letters, numbers "
                "and @/./+/-/_ characters."),
                "invalid"
            ),
        ],
        error_messages={
            "unique": _("A user with that username already exists."),
        })

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    is_email_validated = models.BooleanField(
        _("email_status"),
        default=False,
        help_text=_("Верифікація email"),
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Designates whether this user should be treated as "
                    "active. Unselect this instead of deleting accounts."),
    )

    type = models.CharField(
        max_length=64,
        verbose_name="Тип юзера",
        choices=TYPE_USER,
        blank=True, null=True,
    )

    subscribecode = models.CharField("Код підписки", max_length=256, blank=True, null=True)
    unique_code = models.CharField(max_length=256, unique=True,)
    region = models.CharField("Область", max_length=256, blank=True, null=True)
    verification_type = models.CharField("Тип верифікації", max_length=64, null=True, blank=True)
    signed_on_notifications = models.BooleanField("Підписаний на сповіщення", default=True)
    show_modal = models.BooleanField("Show message", default=False)
    organization = models.ForeignKey(Organization, related_name="user", blank=True, null=True, on_delete=models.CASCADE)

    objects = UserManagerCustom()

    # this stuff is needed to use this model with django auth as a custom user class
    USERNAME_FIELD = "unique_code"
    REQUIRED_FIELDS = []

    def can_done_approving(self, eservice_id):
        is_can = self.eserviceonapproving_set.filter(eservice=eservice_id, done=0,).first()
        if is_can:
            return True
        else:
            return False

    def is_operator(self):
        return self.groups.filter(name="Оператори").exists()

    def has_unreaded_message(self):
        try:
            return Dialog.objects.filter(owner=self).last().messages.filter(read=False).exclude(sender=self)
        except:
            return False

    def operators_unread(self):
        try:
            return Message.objects.filter(read=False).exclude(sender__groups__name__in=["Оператори"])
        except:
            return False

    #чоловік
    def is_male(self):
        if self.identification_code != "0":
            if int(str(self.identification_code)[-2]) % 2 == 0:
                return False
            else:
                return True
    #жінка
    def is_female(self):
        if self.identification_code != "0":
            if int(str(self.identification_code)[-2]) % 2 == 0:
                return True
            else:
                return False

    def __str__(self):
        return self.last_name + " " + self.first_name + " " + self.middle_name

    class Meta:
        verbose_name = "Користувачі"
        verbose_name_plural = "Користувачі"


class ProxyGroup(Group):
    class Meta:
        proxy = True
        verbose_name = "група"
        verbose_name_plural = "групи"


class Log_User(models.Model):
    source = models.TextField(verbose_name="source", null=False, blank=False)
    type = models.TextField(verbose_name="type", null=False, blank=False)
    json_login = models.TextField(verbose_name="json_login", null=False, blank=False)
    date_creation = models.DateTimeField(_("date creation"), default=timezone.now)

    class Meta:
        db_table = "log_login"
        verbose_name = "Log_Login"
        verbose_name_plural = "Log_Login"


class Department(MPTTModel):
    dept_no = models.CharField(_("code"), primary_key=True, max_length=30)
    dept_name = models.CharField(_("name"), unique=True, max_length=150)
    priority = models.IntegerField(default=0, verbose_name="Приорітет для сортування")
    parent = TreeForeignKey("self", null=True, blank=True, related_name="children", db_index=True,
                            verbose_name="Входить у підрозділ", on_delete=models.CASCADE)

    class MPTTMeta:
        order_insertion_by = ["dept_name"]

    class Meta:
        verbose_name = _("department")
        verbose_name_plural = _("departments")
        db_table = "user_departments"
        ordering = ["dept_no"]

    def __str__(self):
        return self.dept_name


class DeptEmp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="emp_no", verbose_name=_("employee"))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, db_column="dept_no", verbose_name=_("department"))
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    priority = models.IntegerField(default=0, verbose_name="Приорітет для сортування")
    from_date = models.DateField(_("from"), default=datetime.now)
    to_date = models.DateField(_("to"), default=get_dept_final_date)

    objects = TemporalQuerySet.as_manager()

    class Meta:
        verbose_name = _("department employee")
        verbose_name_plural = _("department employees")
        db_table = "user_dept_emp"
        unique_together = (("user", "department"),)

    def __str__(self):
        return "{} - {}".format(self.user, self.department)


class DeptManager(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="emp_no", verbose_name=_("employee"))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, db_column="dept_no", verbose_name=_("department"))
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    from_date = models.DateField(_("from"), default=datetime.now)
    to_date = models.DateField(_("to"), default=get_dept_final_date)

    objects = TemporalQuerySet.as_manager()

    class Meta:
        verbose_name = _("department manager")
        verbose_name_plural = _("department managers")
        db_table = "user_dept_manager"
        unique_together = (("user", "department"),)

    def __str__(self):
        return "{} - {}".format(self.user, self.department)

# @receiver(post_save, sender=User, dispatch_uid='DocFlow.users.models.user_post_save_handler')
# def post_save(sender, instance, created, **kwargs):
#     if created:
#         try:
#             group, created = Group.objects.get_or_create(name='Користувачі міськвиконкому')
#             instance.groups.add(group)
#         except:
#             pass
#         instance.is_active = True
#         instance.save()
#
#         admins_emails = list(User.objects.filter(is_superuser=True).values_list('email', flat=True))
#         context = {
#             'id': instance.id,
#             'name': instance.get_full_name or instance.username
#         }
#         subject = 'Зареєстрований новий користувач'
#         template_name = 'new_user.email'
#         send_letter(subject, template_name, context, admins_emails)