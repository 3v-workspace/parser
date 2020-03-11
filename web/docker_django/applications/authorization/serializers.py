from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class BankIdUserSerializer(serializers.ModelSerializer):
    """Серіалізатор для моделі користувача (User).
    """
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "phone",
            "bank_id_token"
        )
        read_only_fields = (
            "id",
            "bank_id_token"
        )
