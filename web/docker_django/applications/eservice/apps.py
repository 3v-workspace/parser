from django.apps import AppConfig


class EServiceApiConfig(AppConfig):
    name = 'eservice'
    icon = '<i class="material-icons">people</i>'
    verbose_name = "Послуги"

    def has_perm(self, user):
        return user.is_superuser