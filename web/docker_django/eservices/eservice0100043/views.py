from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, get_list_or_404
from eservice.models import GeoCity


def city_load(request):
    '''

    Returns: redirect [object]
    '''
    id_parent = request.GET.get("region")
    city_list = GeoCity.objects.filter(parent=id_parent)

    return render(request, "eservice0100043/dropdown/city.html", {
        "city_list": city_list,
    })
