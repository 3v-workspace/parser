import hashlib

from ipware.ip import get_ip
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http.response import HttpResponse

from support.models import Dialog
from eservice.models import EService, Log
from eservice.models import EServiceLog
from system.decorators import group_required
from django.conf import settings

User = get_user_model()

def return_reg_template(request):
    return render(request, "registration/login.html")


def index(request):

    '''
    Returns: render [request, context]
    '''

    operators = User.objects.filter(groups__name="Оператори")
    operators_count = User.objects.filter(groups__name="Оператори").count()
    female = 0
    man = 0

    for item in operators:
        if int(str(item.identification_code)[-2]) % 2 == 0:
            female += 1
        else:
            man += 1
    if operators_count:
        percentage_man = round((man * 100) / operators_count)
        percentage_female = round((female * 100) / operators_count)
    else:
        percentage_man = 0
        percentage_female = 0
    e_services_final = EService.objects.filter(Q(status=7) | Q(status=9)).count()
    e_services_in_work = EService.objects.filter(Q(status=6) | Q(status=8) | Q(status=10)).count()
    e_services = EService.objects.filter(created_by=request.user).order_by("-id").distinct()

    dict_with_log = []

    if e_services:
        e_services_last_id = e_services[0].id
        logs = EServiceLog.objects.filter(eservice=e_services_last_id).order_by("-id")
        logs_date = EServiceLog.objects.filter(eservice=e_services_last_id).order_by("-id").values_list("created_at", flat=True)
        list_date = [dt.date() for dt in logs_date]

        for item in set(list_date):
            day = EServiceLog.objects.filter(eservice=e_services_last_id, created_at__date=item)
            date = item

            time_obj = []

            for item in day:
                time_obj.append({"val_time": item.created_at.time(), "desk": item.activity, "user": item.created_by})

            dict_with_log.append({"date": {"val_date": date, "time": time_obj}})
    else:
        e_services_last_id = None
    return render(request, "frontend/index.html", {
        "e_services": e_services,
        "percentage_man": percentage_man,
        "percentage_female": percentage_female,
        "e_services_final": e_services_final,
        "e_services_in_work": e_services_in_work,
        "dict_with_log": dict_with_log,
        "e_services_last_id": e_services_last_id,
        "operators_count": operators_count,
    })


def elements(request):

    '''
    Returns: render [request, context]
    '''

    return render(request, "frontend/elements.html")

def documentation(request):

    '''
    Returns: render [request, context]
    '''

    return render(request, "frontend/documentation.html")

def infinitive(request):
    # numbers_list = range(1, 1000)
    numbers_list = Dialog.objects.all()
    page = request.GET.get("page", 1)
    paginator = Paginator(numbers_list, 2)
    try:
        numbers = paginator.page(page)
    except PageNotAnInteger:
        numbers = paginator.page(1)
    except EmptyPage:
        numbers = paginator.page(paginator.num_pages)
    return render(request, "infinitive.html", {
        "numbers": numbers,
    })


def robots(request):
    data = open("robots.txt", "rb").read()
    return HttpResponse(data, content_type="text/plain")