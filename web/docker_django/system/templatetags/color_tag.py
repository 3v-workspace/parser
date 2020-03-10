from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='color_tag')
def color_tag(percentage, arg):
    if int(percentage) < 34:
        return 'bg-red'
    elif 34 < int(percentage) < 75:
        return 'bg-orange'
    elif 75 < int(percentage) <= 100:
        return 'bg-green'
    else:
        return False
