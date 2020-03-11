from django.apps import AppConfig


class SupportConfig(AppConfig):
    name = 'support'
    icon = '<i class="material-icons">people</i>'
    verbose_name = "Месенджер"

    def has_perm(self, user):
        return user.is_superuser