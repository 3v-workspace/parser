from django.contrib import admin

from eservice.models import EServiceMeta


@admin.register(EServiceMeta)
class EServiceMetaAdmin(admin.ModelAdmin):
    exclude = ['created_at']
