from django import template
from django.contrib.auth.models import Group
from eservice.models import EServiceStar

register = template.Library()


@register.filter(name='exist_estimation')
def exist_estimation(user, eservice_id):

    try:
        exist_estimation = EServiceStar.objects.get(eservice_id=eservice_id, created_by=user)
    except EServiceStar.DoesNotExist:
        exist_estimation = False

    if exist_estimation:
        average_value = exist_estimation.average_value
    else:
        average_value = None

    return average_value