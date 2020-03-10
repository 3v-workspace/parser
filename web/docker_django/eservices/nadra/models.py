from django.contrib.postgres.fields import ArrayField
from django.db import models

from eservice.models import EService


class NadraModel(EService):
    pib = models.CharField(verbose_name="ПІБ", max_length=200, null=True, blank=True)
    info_person = models.CharField(
        verbose_name="Інформація про особу підписанта Угоди про умови користування надрами  (посада та ПІБ)",
        max_length=200, null=True, blank=True)
    email = models.CharField(verbose_name="Email", max_length=200, null=True, blank=True)
    inn = models.CharField(verbose_name="Ідентифікаційний номер", max_length=200, null=True, blank=True)
    place = models.CharField(verbose_name="Місцезнаходження", max_length=200, null=True, blank=True)
    info_document = models.CharField(verbose_name="Інформація про документ", max_length=200, null=True, blank=True)
    phone = models.CharField(verbose_name=" Телефон", max_length=200, null=True, blank=True)
    organ = models.CharField(verbose_name="Відповідальний орган", max_length=200, null=True, blank=True)
    comment = models.TextField(verbose_name="Докладний опис", null=True)
    signature = models.TextField(verbose_name="Підпис", null=True)

    class Meta:
        db_table = 'nadra'
        verbose_name = 'nadra'
        verbose_name_plural = 'nadra'


class Areas(models.Model):
    nadra = models.ForeignKey(NadraModel, on_delete=models.CASCADE)

    poly = ArrayField(
        ArrayField(
            models.FloatField(),
            size=2,
        )
    )
