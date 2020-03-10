import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from nadra.frontend.forms import EServiceFrontendFormNadra
from nadra.models import NadraModel, Areas

from eservice.models import EServiceFile
from eservice.models import EServiceType, EServiceLog, EService
from eservice.models import Log

from eservice.models import EServiceSign
from system.email_sender import send_letter
from system.libs import validate_file_extension


def create(request, created_by_ip):
    if True:
        if request.method == 'POST':
            form = EServiceFrontendFormNadra(request.POST)
            # fill a model from a POST
            if form.is_valid():
                e_service = form.save(commit=False)
                e_service.created_by_id = request.user.id
                e_service.created_by_ip = created_by_ip
                e_service.type = EServiceType.objects.get(pk=3)
                e_service.pib = str(request.user)
                e_service.inn = request.user.identification_code
                if EService.objects.all():
                    last_element = EService.objects.latest('id').id
                else:
                    last_element = 0
                e_service.internal_id = "{}-СЗ".format(last_element + 1)
                e_service.save()

                Log(eservice_id=e_service.id, action="Послугу було створено" + ' - ' + request.user.last_name
                                                     + ' ' + request.user.first_name,
                    user=request.user).write()

                # messages.success(request, "Послугу було успішно створено")
                # if request.FILES:
                #     for file in request.FILES.getlist('file'):
                #         validate_file_extension(file)
                #         filename = file.name
                #         ext = filename.split('.')[-1]
                #         filename = "{}__{}__{:%d-%m-%Y}__ID-{}.{}".format(
                #                 e_service.type.title,
                #                 e_service.internal_id.replace("/", "."),
                #                 e_service.created_at,
                #                 e_service.id, ext)
                #
                #         mime = file.content_type
                #         size = file.size
                #
                #         eservice_file = EServiceFile.objects.create(eservice=e_service, file=file, author=request.user,\
                #                                                     mime=mime, size=size, filename = filename)
                #         eservice_file.save()

                return redirect('/eservice/nadra/step-2/' + str(e_service.id))
            else:
                return render(request, 'nadra/frontend/create.html', {'form': form})

        else:
            form = EServiceFrontendFormNadra(
                initial={'pib': request.user, 'inn': request.user.identification_code, 'phone': request.user.phone})
            return render(request, 'nadra/frontend/create.html', {'form': form})
    else:
        redirect('accounts/signup')


def step_2(request, eservice_id):
    if request.is_ajax() and request.method == 'POST':

        post = json.loads(request.body.decode('utf-8'))

        polygons = post['polygons']

        nadra = NadraModel.objects.get(eservice_ptr_id=eservice_id)

        for polygon in polygons:
            poly = polygon.get('polygon')

            if (poly):
                pid = polygon.get('id', -1)
                if (pid == -1):
                    Areas.objects.create(poly=poly[0], nadra_id=nadra.id).save()
                else:
                    Areas.objects.filter(pk=pid).update(poly=poly[0])

        result = {
            'success': 1,
            'messages': 'Область було успішно додано',
            'redirect': '/eservice/nadra/step-3/' + str(eservice_id)
        }

        # messages.success(request, "Область було успішно додано")

        return JsonResponse(result)
        # return redirect('/eservice/step-3/' + str(eservice_id))
    else:
        return render(request, 'nadra/frontend/create_step_2.html', {})


def step_3(request, eservice_id):
    if request.method == 'POST':
        comment = request.POST.get('comment')
        nadra = NadraModel.objects.get(eservice_ptr_id=eservice_id)
        nadra.comment = comment
        nadra.save()
        return redirect('/eservice/nadra/step-4/' + str(eservice_id))
    else:
        return render(request, 'nadra/frontend/create_step_3.html')


def step_4(request, eservice_id):
    if request.method == 'POST':
        e_service = EService.objects.get(id=eservice_id)
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

                eservice_file = EServiceFile.objects.create(eservice=e_service, file=file, author=request.user, \
                                                            mime=mime, size=size, filename=filename)
                eservice_file.save()
        return redirect('/eservice/nadra/step-5/' + str(eservice_id))
        # return redirect('/eservice/eservice_signature/' + str(e_service.id))
    else:
        form = EServiceFrontendFormNadra()
        return render(request, 'nadra/frontend/create_step_4.html', {'form': form})


def step_5(request, eservice_id):
    e_service = get_object_or_404(EService, pk=eservice_id)
    redirect_signature = '/eservice/nadra/step-6/' + str(eservice_id)
    return render(request, "nadra/frontend/create_step_5.html", {"redirect_signature": redirect_signature,
                                                                 "eservice_type": e_service.type.model,
                                                                 "eservice_id": eservice_id,
                                                                 "apps": e_service.type.controller
                                                                 })


def step_6(request, eservice_id):
    e_service = get_object_or_404(EService, pk=eservice_id)
    return render(request, "nadra/frontend/create_step_6.html", {"id_test_service": e_service.id,
                                                                 "eservice_type": e_service.type.model,
                                                                 "apps": e_service.type.controller
                                                                 })


def view(request, eservice_id, helper):
    dict_with_log = []
    e_service = get_object_or_404(NadraModel, pk=eservice_id)
    logs = EServiceLog.objects.filter(eservice=e_service).order_by('-id')
    logs_date = EServiceLog.objects.filter(eservice=e_service).order_by('-id').values_list('created_at', flat=True)
    list_date = [dt.date() for dt in logs_date]

    for item in set(list_date):
        day = EServiceLog.objects.filter(eservice=e_service, created_at__date=item)
        date = item

        time_obj = []

        for item in day:
            time_obj.append({'val_time': item.created_at.time(), 'desk': item.activity, 'user': item.created_by})

        dict_with_log.append({'date': {'val_date': date, 'time': time_obj}})

    operations = []  # Відправити на доопрацювання, Видалити, Редагувати
    try:
        EServiceSign.objects.get(eservice=e_service, user=request.user)
        is_send_to_another = True
    except:
        is_send_to_another = False

    return render(request, 'nadra/frontend/view.html', {
        'e_service': e_service,
        'is_send_to_another': is_send_to_another,
        'dict_with_log': dict_with_log,
        'operations': operations,
        'helper': helper
    })


def send_to_another(request, eservice_id):
    """
    :param request: contains `id_service_request`, `certificate`
    :return: status, error, ppszHash, ppbHash
    """

    from crypto_info.views import send_to_another_sign

    if request.POST:
        if request.POST.get('email', False):
            email = request.POST.get('email', False)
            dict_sign = {'id': request.user.id, 'eservice_id': eservice_id, 'email': email}
            encoded = send_to_another_sign(request, dict_sign)

            send_letter('Кабінет державного органу. Підпис документу', 'email_sign.email',
                        {'encoded': encoded.decode('utf-8'), 'uid': '', 'token': '', 'domain': SITE_URL}, email)
        else:
            messages.add_message(request, messages.ERROR,
                                 'Ви не вказали email, повідомлення не було відправлене')
            redirect('/eservice/nadra/step-5/' + str(eservice_id))

    # e_service = get_object_or_404(EService, pk=eservice_id)
    # redirect_signature = '/eservice/nadra/step-6/' + str(eservice_id)
    messages.add_message(request, messages.SUCCESS,
                         'Ваше запрошення на підписання було відправлено')
    return redirect('/eservice/nadra/step-5/' + str(eservice_id))
    # return render(request, "nadra/frontend/create_step_5.html", {"eservice_id": eservice_id, })

