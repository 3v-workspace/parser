from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from eservice.models import EServiceType, EServiceLog, EService

from eservice.models import Log
from system.libs import validate_file_extension
from eservice0100043.models import EService0100043

from eservice0100043.frontend.forms import EServiceFrontendForm0100043

from eservice.models import EServiceFile


def create(request, created_by_ip):
    if True:
        if request.method == 'POST':
            form = EServiceFrontendForm0100043(request.POST, request.FILES)
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

                Log(eservice_id=e_service.id, action="Послугу було створено" + ' - ' + request.user.last_name
                                                     + ' ' + request.user.first_name,
                    user=request.user).write()

                messages.success(request, "Послугу було успішно створено")
                if request.FILES:
                    for file in request.FILES.getlist('file'):
                        validate_file_extension(file)
                        filename = file.name
                        ext = filename.split('.')[-1]
                        filename = "{}__{}__{:%d-%m-%Y}__ID-{}.{}".format(
                                e_service.type.title,
                                e_service.internal_id.replace("/", "."),
                                e_service.created_at,
                                e_service.id, ext)

                        mime = file.content_type
                        size = file.size

                        eservice_file = EServiceFile.objects.create(eservice=e_service, file=file, author=request.user,\
                                                                    mime=mime, size=size, filename = filename)
                        eservice_file.save()

                return redirect("/eservice/eservice_signature/" + str(e_service.id))
            else:
                return render(request, "eservice0100043/frontend/create.html", {"form": form})

        else:
            form = EServiceFrontendForm0100043()
            return render(request, "eservice0100043/frontend/create.html", {
                "form": form,
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
            time_obj.append({"val_time": item.created_at.time(), "desk": item.activity, "user": item.created_by})

        dict_with_log.append({"date": {"val_date": date, "time": time_obj}})


    operations = [] # Відправити на доопрацювання, Видалити, Редагувати

    return render(request, "eservice0100043/frontend/view.html", {
        "e_service": e_service,
        "dict_with_log": dict_with_log,
        "operations": operations,
        "helper": helper
    })


