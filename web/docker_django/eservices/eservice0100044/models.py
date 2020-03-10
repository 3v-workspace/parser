# Only for developing purposes
from datetime import datetime
from django.db import models
from eservice.models import EService

from eservice.models import EServiceMeta


class EService0100044(EService):
    comment2 = models.TextField(verbose_name="Докладний опис2", null=True)
    type_license2 = models.ForeignKey(EServiceMeta, null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='type_license_meta2')
    payment2 = models.ForeignKey(EServiceMeta, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='payment_meta2')
    region2 = models.CharField(verbose_name="Область2", max_length=200, null=True, blank=True)
    city2 = models.CharField(verbose_name="Місто2", max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'eservice0100044'
        verbose_name = 'eservice0100044'
        verbose_name_plural = 'eservice0100044'