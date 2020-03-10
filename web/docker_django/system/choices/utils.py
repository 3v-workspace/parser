from django import template

from system.choices.models import (
    Choices, Field,
    CHOICES_LIST,
)


def get_choice_key(instance, field_name) -> str:
    '''
    Использование:
        get_choice_key(object, "field")
    Возвращает ключ чойса по значению поля
    '''
    current_value = getattr(instance, field_name)

    choices:Choices or None = None
    for choice in CHOICES_LIST:
        try:
            # Если такого значения нету - вызовет исключение
            choice.instances.index((instance._meta.model, field_name))
            choices = choice
            break
        except ValueError:
            continue

    if not choices:
        raise Exception("Suitable Choices not found!")

    for field in choices.fields:
        if field.id == current_value:
            return field.key

    return ""