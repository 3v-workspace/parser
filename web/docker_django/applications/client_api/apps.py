from django.apps import AppConfig


class ClientApiConfig(AppConfig):
    name = 'client_api'
    icon = '<i class="material-icons">people</i>'
    verbose_name = "Внутрішня інтероперабельність. Simple Usage API"

    def has_perm(self, user):
        return user.is_superuser