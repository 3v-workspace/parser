from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, get_list_or_404
from django.urls import reverse
from pure_pagination import Paginator, PageNotAnInteger

from eservice.models import EServiceOnApproving
from eservice.models import EServiceType, EServiceLog, EService, Log
from eservice0100043.backend.forms import EServiceBackendForm0100043
from eservice0100043.models import EService0100043

User = get_user_model()

def create(request, created_by_ip):
    if True:
        if request.method == "POST":
            form = EServiceBackendForm0100043(request.POST, request.FILES)
            # fill a model from a POST
            if form.is_valid():
                e_service = form.save(commit=False)
                e_service.created_by_id = request.user.id
                e_service.created_by_ip = created_by_ip
                e_service.type = EServiceType.objects.get(pk=1)
                if EService.objects.all():
                    last_element = EService.objects.latest("id").id
                else:
                    last_element = 0
                e_service.internal_id = "{}-СЗ".format(last_element + 1)
                e_service.save()

                Log(
                    eservice_id=e_service.id,
                    action=f"Послугу було створено - {request.user.last_name} {request.user.first_name}",
                    user=request.user
                ).write()

                # "/backend/eservice/update/"+str(last_element+1)+"/2")
                return redirect(reverse("create_eservice",
                                        args=(last_element+1, 2)))
            else:
                return render(request, "eservice0100043/backend/create.html", {
                    "form": form,
                })
        else:
            form = EServiceBackendForm0100043()
            e_service_type = EServiceType.objects.get(pk=1)
            return render(request, "eservice0100043/backend/create.html", {
                "form": form,
                "eservice_type": e_service_type,
            })
    else:
        redirect("accounts/signup")


def view(request, eservice_id, helper):
    dict_with_log = []
    e_service = get_object_or_404(EService0100043, pk=eservice_id)
    logs = EServiceLog.objects.filter(eservice=e_service).order_by("-id")
    logs_date = EServiceLog.objects.filter(eservice=e_service).order_by("-id").values_list("created_at", flat=True)
    list_date = [dt.date() for dt in logs_date]

    for item in set(list_date):
        day = EServiceLog.objects.filter(eservice=e_service, created_at__date=item)
        date = item

        time_obj = []

        for item in day:
            time_obj.append({
                "val_time": item.created_at.time(),
                "desk": item.activity,
                "user": item.created_by,
            })

        dict_with_log.append({
            "date": {
                "val_date": date,
                "time": time_obj,
            }
        })

    operations = [] # Відправити на доопрацювання, Видалити, Редагувати

    bosses = User.objects.filter(groups__name="Погоджувачі")
    try:
        page = request.GET.get("page", 1)
    except PageNotAnInteger:
        page = 1

    # p = Paginator(logs, 5, request=request)
    # logs = p.page(page)

    approvers = EServiceOnApproving.objects.filter(eservice=e_service)
    return render(request, "eservice0100043/backend/view.html", {
        "e_service": e_service,
        "approvers": approvers,
        "bosses": bosses,
        "logs": logs,
        "dict_with_log": dict_with_log,
        "operations": operations,
        "helper": helper
    })


def update(request, eservice_id, created_by_ip, step, helper):
    e_service = get_object_or_404(EService0100043, pk=eservice_id)
    if step == 1:
        if request.method == "POST":
            form = EServiceBackendForm0100043(request.POST, request.FILES, instance=e_service)
            # fill a model from a POST
            if form.is_valid():
                e_service = form.save(commit=False)
                e_service.created_by_id = request.user.id
                e_service.created_by_ip = created_by_ip
                e_service.type = EServiceType.objects.get(pk=1)
                e_service.save()

                return redirect(
                    # "/backend/eservice/update/"+str(e_service.id)+"/3"
                    reverse("update_eservice",
                            args=(e_service.id, 3))
                )
            else:
                return render(request, "eservice0100043/backend/update_step1.html", {
                    "form": form,
                })
        else:
            form = EServiceBackendForm0100043(instance=e_service)
            return render(request, "eservice0100043/backend/update_step1.html", {
                "form": form,
                "e_service": e_service,
                "document_object": e_service,
            })
    elif step == 2:
        bosses = User.objects.filter(groups__name="Погоджувачі")
        return render(request, "eservice0100043/backend/update_step2.html", {
            "bosses": bosses,
            "e_service": e_service,
            "helper": helper,
            "redirect_url_step3": reverse("update_eservice",
                                          args=(e_service.id, 2)) #"/eservice/update/{}/2".format(e_service.id)})
        })

    elif step == 4:
        return render(request, "eservice0100043/backend/update_step4.html", {
            "e_service": e_service,
            "helper": helper,
            "redirect_url_step4": reverse("update_eservice",
                                          args=(e_service.id, 4)) #"/eservice/update/{}/4".format(e_service.id)})
        })

    else:
        return redirect("/")
