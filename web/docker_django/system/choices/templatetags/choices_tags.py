from django import template

from system.choices.models import (
    Choices, Field,
    CHOICES_LIST,
)
from system.choices import utils

register = template.Library()


@register.filter
def get_choice_key(instance, field_name) -> str:
    '''
    Использование:
        {{ object|get_choice_key:"field" }}
    Возвращает ключ чойса по значению поля
    '''
    return utils.get_choice_key(instance, field_name)