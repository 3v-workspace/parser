from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='final_status')
def final_status(user, status):
    if "final" in status.attr:
        return True
    else:
        return False