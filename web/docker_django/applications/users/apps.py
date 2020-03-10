from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "users"
    icon = "<i class=\"material-icons\">people</i>"
    verbose_name = "Штатний розпис"

    def has_perm(self, user):
        return user.is_superuser
