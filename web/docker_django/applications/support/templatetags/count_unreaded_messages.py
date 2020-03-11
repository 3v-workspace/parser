from django import template
from django.contrib.auth.models import Group
from eservice.models import EServiceStar
from support.models import Dialog

register = template.Library()


@register.filter(name='unreaded_chat')
def unreaded_chat(dialog, opponent_id):
    dialog = Dialog.objects.get(id=dialog.id)
    unreaded_messages = dialog.messages.filter(read=False).exclude(sender_id=opponent_id)
    return unreaded_messages
    # try:
    #     exist_estimation = DocumentStar.objects.get(document_id=document_id, created_by=user)
    # except DocumentStar.DoesNotExist:
    #     exist_estimation = False
    #
    # if exist_estimation:
    #     average_value = exist_estimation.average_value
    # else:
    #     average_value = None
    #
    # return average_value