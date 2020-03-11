import simplejson as simplejson
from django.db.models import ForeignKey
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.apps import apps
import base64
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.
from eservice.models import EService

from eservice0100043.models import EService0100043
from eservice.models import EServiceType
from stronghold.decorators import public
from django.contrib.auth import get_user_model
from client_api.models import ClientApi
from client_api.decorators import custom_authenticate
from client_api.models import ClientApiEServiceField, ClientApiEService

from applications.client_api.config import config_dict

User = get_user_model()


def admin_change_field(request, eservice_id):
    """Формування полів для адмінки

    Args:
        request: об'єкт Django request, eservice_id

    Returns: HttpResponse(json)
        """

    eservice_type = get_object_or_404(EServiceType, pk=eservice_id)

    eservice_model = eservice_type.model
    apps_doc = eservice_type.controller

    model = apps.get_model(apps_doc, eservice_model)
    field_list = []
    for f in model._meta.get_fields():
        if hasattr(f, "verbose_name"):
            field_list.append((f.name, f.verbose_name))

    json_metric = simplejson.dumps({"field_list": field_list, })
    return HttpResponse(json_metric, content_type="application/json")


class EServiceList(APIView):

    def get(self, request, eservice_type, inn):
        user = User.objects.get(identification_code=inn)
        eservice_type_obj = EServiceType.objects.get(title=eservice_type)
        eservice = EService.objects.filter(type=eservice_type_obj, created_by=user)
        json = {}
        for item in eservice:
            json["id"] = item.id
            json["title"] = item.title

        return Response(json)





@public
@custom_authenticate
def eservice_list(request, eservice_type, inn, *args, **kwargs):
    """АПІ.

    Args:
        request: об'єкт Django request, eservice_type, inn

    Returns: HttpResponse(json)
        """

    # FIXME: typo in masseges -> messages
    client = kwargs['user']
    try:
        user = User.objects.get(identification_code=inn)
    except:
        return HttpResponse(simplejson.dumps({"masseges": "Не знайдено ідентифікаційний код"}), content_type="application/json")

    try:
        eservice_type_obj = EServiceType.objects.get(title=eservice_type)
    except:
        return HttpResponse(simplejson.dumps({"masseges": "Не знайдено тип послуги"}), content_type="application/json")

    client_eservice_type = ClientApiEService.objects.filter(client=client, ).values_list("eservice", flat=True)

    if eservice_type_obj.id in client_eservice_type:
        eservice = EService.objects.filter(type=eservice_type_obj, created_by=user)
    else:
        return HttpResponse(simplejson.dumps({"masseges": "У Вас немає доступу до цього типу послуги"}),
                            content_type="application/json")

    eservice_dict = []
    for item in eservice:
        eservice_dict.append({"id": item.id, "title": item.title})
    return HttpResponse(simplejson.dumps(eservice_dict), content_type="application/json")


@public
@custom_authenticate
def eservice_card(request, eservice_type, inn, card_id, *args, **kwargs):
    """АПІ.

    Args:
        request: об'єкт Django request, eservice_type, inn

    Returns: HttpResponse(json)
        """

    client = kwargs['user']


    try:
        eservice_type_obj = EServiceType.objects.get(title=eservice_type)
    except:
        return HttpResponse(simplejson.dumps({"masseges": "Не знайдено тип послуги"}),
                            content_type="application/json")

    try:
        client_api_eservice = ClientApiEService.objects.get(eservice=eservice_type_obj, client=client, )
    except:
        return HttpResponse(simplejson.dumps({"masseges": "У Вас немає доступу до цього типу послуги"}),
                            content_type="application/json")

    clien_api_fields2 = ClientApiEServiceField.objects.filter(client_api_eservice=client_api_eservice, )


    clien_api_fields = ClientApiEServiceField.objects.filter(client_api_eservice=client_api_eservice,).values_list("field", flat=True)


    eservice_model = eservice_type_obj.model
    apps_doc = eservice_type_obj.controller
    model = apps.get_model(apps_doc, eservice_model)

    eservice_object = model.objects.get(pk=card_id)
    client_api_list =  list(clien_api_fields)

    for i, item in enumerate(client_api_list):
        field_type = eservice_object._meta.get_field(str(item)).get_internal_type()

        if field_type == "ForeignKey":
            client_api_list[i] = config_dict[str(model.__name__)][str(item)]

    eservice = model.objects.values(*client_api_list).get(pk=card_id)

    doc_dict = {}

    list_value = []

    for item in config_dict[str(model.__name__)]:
        list_value.append(config_dict[str(model.__name__)][str(item)])

    for item in eservice:
        if str(item) in list_value:
            doc_dict[item.split('__')[0]] = str(eservice[item])
        else:
            doc_dict[item] = str(eservice[item])

    return HttpResponse(simplejson.dumps(doc_dict), content_type="application/json")

