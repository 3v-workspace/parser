import json

from django.http import JsonResponse
from django.shortcuts import render

from eservice.models import GeoCity
from nadra.models import NadraModel, Areas


def city_load(request):
    '''

    Returns: redirect [object]
    '''
    id_parent = request.GET.get('region')
    city_list = GeoCity.objects.filter(parent=id_parent)

    return render(request, 'nadra/dropdown/city.html', {'city_list': city_list})


def areas_load(request):
    result = {
        'success': 0,
        'messages': 'Не вірний запит'
    }

    if request.is_ajax() and request.method == 'POST':
        # post = request.body.decode('utf-8') # may be need .replace('\'', '\"') for valid json
        post = json.loads(request.body)

        eservice_id = post['eservice_id']

        nadra = NadraModel.objects.get(eservice_ptr_id=eservice_id)

        areas = Areas.objects.filter(nadra_id=nadra.id).values('id', 'poly')

        result = {
            'success': 1,
            'eservice_id': eservice_id,
            'polygons': list(areas),
        }


    return JsonResponse(result)
