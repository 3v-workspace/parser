from django.db import models
from eservice.models import EService
from eservice.models import EServiceMeta


class EService0100043(EService):
    comment = models.TextField(verbose_name="Докладний опис", null=True)
    type_license = models.ForeignKey(EServiceMeta, null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='type_license_meta')
    payment = models.ForeignKey(EServiceMeta, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='payment_meta')
    region = models.CharField(verbose_name="Область", max_length=200, null=True, blank=True)
    city = models.CharField(verbose_name="Місто", max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'eservice0100043'
        verbose_name = 'eservice0100043'
        verbose_name_plural = 'eservice0100043'