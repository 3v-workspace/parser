import datetime
import json

from celery.utils.time import timezone
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from ipware.ip import get_ip

from eservice.models import EService, Log, EServiceStatus, EServiceOnApproving, EServiceMeta, EServiceStar
from signature.views import get_key_info
from users.models import DeptEmp
from system.email_sender import send_letter

User = get_user_model()

def index_backend(request):
    '''
    Returns: redirect [object]

    '''
    filter_time = request.GET.get('filter')
    if filter_time:
        data_now = datetime.datetime.now()
        filter_date_dict = {'last_week': 7, 'last_month': 31,}
        day_delta = data_now - datetime.timedelta(days=filter_date_dict[filter_time])
    e_services = EService.objects.all().order_by('-id')[:5]

    if filter_time:
        e_services_all = EService.objects.filter(created_at__gte=day_delta).count()
        # e_services_in_work = EService.objects.filter(Q(status=6) | Q(status=8) | Q(status=10)).count()
        e_services_in_rejected = EService.objects.filter(created_at__gte=day_delta, status=7).count()
        e_services_in_work = EService.objects.filter(created_at__gte=day_delta, status=6).count()
        e_services_on_approval = EService.objects.filter(created_at__gte=day_delta, status=8).count()
        e_services_done = EService.objects.filter(created_at__gte=day_delta, status=9).count()
        e_services_on_refinement = EService.objects.filter(created_at__gte=day_delta, status=10).count()
        e_services_final = EService.objects.filter(Q(status=7) | Q(status=9)).count()
    else:
        e_services_all = EService.objects.all().count()
        # e_services_in_work = EService.objects.filter(Q(status=6) | Q(status=8) | Q(status=10)).count()
        e_services_in_rejected = EService.objects.filter(status=7).count()
        e_services_in_work = EService.objects.filter(status=6).count()
        e_services_on_approval = EService.objects.filter(status=8).count()
        e_services_done = EService.objects.filter(status=9).count()
        e_services_on_refinement = EService.objects.filter(status=10).count()
        e_services_final = EService.objects.filter(Q(status=7) | Q(status=9)).count()
    if e_services_all != 0:
        percentage_in_work = round((e_services_in_work*100)/e_services_all)
        percentage_in_rejected = round((e_services_in_rejected*100)/e_services_all)
        percentage_on_approval = round((e_services_on_approval*100)/e_services_all)
        percentage_done = round((e_services_done*100)/e_services_all)
        percentage_on_refinement = round((e_services_on_refinement*100)/e_services_all)
    else:
        percentage_in_work = 0
        percentage_in_rejected = 0
        percentage_on_approval = 0
        percentage_done = 0
        percentage_on_refinement = 0

    return render(request, 'backend/index.html', {
        'e_services': e_services,
        'e_services_in_work': e_services_in_work,
        'e_services_all': e_services_all,
        'e_services_final': e_services_final,
        'percentage_in_work': percentage_in_work,
        'percentage_in_rejected': percentage_in_rejected,
        'percentage_on_approval': percentage_on_approval,
        'percentage_done': percentage_done,
        'percentage_on_refinement': percentage_on_refinement,
    })

def stars_module(request):
    # Stars Section
    star = EServiceStar.objects.all().count()

    context = {
        'star': star,
    }
    return render(request, 'backend/stars_module.html', context)

def eservices_bystar(request):
    if request.GET.get('stars'):
        star_option = request.GET.get('stars')
        if star_option == 'maximum':
            desciption = '8-10 зірок'
            eservices_stars = EServiceStar.objects.filter(average_value__gte=8).values_list('eservice_id', flat=True)
        elif star_option == 'good':
            desciption = '6-8 зірок'
            eservices_stars = EServiceStar.objects.filter(average_value__gte=6, average_value__lt=8).values_list('eservice_id', flat=True)
        elif star_option == 'average':
            desciption = '4-6 зірок'
            eservices_stars = EServiceStar.objects.filter(average_value__gte=4, average_value__lt=6).values_list('eservice_id', flat=True)
        elif star_option == 'bad':
            desciption = '2-4 зірки'
            eservices_stars = EServiceStar.objects.filter(average_value__gte=2, average_value__lt=4).values_list('eservice_id', flat=True)
        else:
            desciption = 'нижче 2 зірок'
            eservices_stars = EServiceStar.objects.filter(average_value__lt=2).values_list('eservice_id', flat=True)
        eservices = EService.objects.filter(id__in=eservices_stars)
        return render(request, 'backend/eservices_by_stars.html', {"eservices":eservices, 'desciption':desciption})
    else:
        return redirect('/backend')

def eservices(request):

    """Всі послуги організації

    Args:
        request: об'єкт Django request.

    Returns:
        render [object]
    """

    # ======Statuses======#
    if request.GET.get('status'):
        if request.GET.get('status') != 'all':
            status = request.GET.get('status')
            request.session['status'] = status
            if status == 'rejected':
                e_services = EService.objects.filter(status=7)
            elif status == 'confirmation':
                e_services = EService.objects.filter(status=8)
            elif status == 'processing':
                e_services = EService.objects.filter(status=6)
            elif status == 'done':
                e_services = EService.objects.filter(status=9)
            else:
                e_services = EService.objects.all()

        else:
            if "status" in request.session:
                del request.session['status']
                e_services = EService.objects.all()
            else:
                e_services = None

    else:
        e_services = EService.objects.all()

    return render(request, 'backend/eservices.html', {
        'e_services': e_services,
    })


def my_eservices(request):

    """Мої послуги - послуги до яких має відношення поточний користувач

    Args:
        request: об'єкт Django request.

    Returns:
        render [object]
    """
    my_e_services = EService.objects.filter(eserviceonapproving__assign_to=request.user,).distinct()
    # ======Statuses======#
    if request.GET.get('status'):
        if request.GET.get('status') != 'all':
            status = request.GET.get('status')
            request.session['status'] = status
            if status == 'rejected':
                my_eservices = my_e_services.filter(status=7)
            elif status == 'confirmation':
                my_eservices = my_e_services.filter(status=8)
            elif status == 'processing':
                my_eservices = my_e_services.filter(status=6)
            elif status == 'done':
                my_eservices = my_e_services.filter(status=9)
            else:
                my_eservices = my_e_services

        else:
            if "status" in request.session:
                del request.session['status']
                my_eservices = my_e_services

    else:
        my_eservices = EService.objects.filter(eserviceonapproving__assign_to=request.user,).distinct()

    return render(request, 'backend/my_eservices.html', {
        'my_e_services': my_e_services,
    })


def not_processed_eservice(request):
    """Необроблені користувачем послуги

    Args:
        request: об'єкт Django request.

    Returns:
        render [object]
    """

    user = request.user
    e_services = EService.objects.filter(
        # Q(resolutioner=user, resolutindex_backendioner_viewed=0) |
        Q(status=6) |
        Q(eserviceonapproving__assign_to=user, eserviceonapproving__viewed=0,)).distinct()
    return render(request, 'backend/not_processed_eservice.html', {'e_services': e_services})


def backend_eservice_create(request):
    """Вибір типу послуги

    Args:
        request: об'єкт Django request.

    Returns:
        render [object]
    """
    return render(request, 'eservice/backend/eservices_list.html', {})


def create_eservice_backend(request, eservice_type='dev'):
    """Створення послуги. Передаємо тип послуги при створенні нового послуги,
    система автоматично підвантажує обслуговуючий коннектор типу

    Args:
        request: об'єкт Django request, eservice_type

    Returns:
        views.create
    """
    views = getattr(__import__(eservice_type+'.backend', fromlist=['views']), 'views')
    created_by_ip = get_ip(request)
    return views.create(request, created_by_ip)


def delete_eservice_backend(request, eservice_id):
    """Видалення послуги.

        Args:
            request: об'єкт Django request, eservice_id

        Returns:
            views.create
    """
    eservice = get_object_or_404(EService.all, pk=eservice_id)

    if eservice.created_by == request.user or request.user.is_allowed_group('Адміністратори'):
        if eservice.status.id in [4, 12]:  # Чернетка чи послугу було повернуто на виправлення помилок
            try:
                eservice.delete()
                Log(eservice_id=eservice_id, action="Послугу №{} було успішно видалено".format(eservice_id),
                    user=request.user).write()
                messages.success(request, "Послугу видалено")
                return redirect('/my_eservices/')
            except ObjectDoesNotExist as error:
                return HttpResponse("При видалення послуги №{}, відбулась помилка: {}".format(eservice_id, error))
        else:
            return PermissionDenied(
                "Послуги у статусі '{}' не можуть бути видалені. Звреніться до адміністратора системи".format(
                    eservice.status.title))
    else:
        return PermissionError("Вам не дозволено видаляти послугу. Зверніться до адміністратора системи")


# Таким чином передаємо тип послуги при редагуванні нового послуги
# система автоматично підвантажує обслуговуючий коннектор типу
def update_eservice_backend(request, eservice_id, step):
    """Редагування послуги. Передаємо тип послуги при редагуванні нового послуги
    система автоматично підвантажує обслуговуючий коннектор типу

    Args:
        request: об'єкт Django request, eservice_id, step

    Returns:
        views.update
    """

    # eservice = get_object_or_404(eservice, id=eservice_id)
    eservice = get_object_or_404(EService, id=eservice_id)

    # перевіряємо, чи користувач має право правити послугу
    if eservice.created_by != request.user:
        if not request.user.is_allowed_group("Адміністратори") or not request.user.is_allowed_group("Загальний відділ"):
            return HttpResponseForbidden()

    type = eservice.type.controller

    # views = getattr(__import__(type, fromlist=['views']), 'views')

    views = getattr(__import__(type+'.backend', fromlist=['views']), 'views')

    created_by_ip = get_ip(request)

    # eservice_permissions = {
    #     'can_set_eservice_to_work_and_return_to_edit': request.user.can_set_eservice_to_work_and_return_to_edit(
    #         eservice_id),
    #     'can_done_formalisation': request.user.can_done_formalisation(eservice_id),
    #     'can_edit': request.user.can_edit(eservice_id),
    #     'can_approve': request.user.can_done_approving(eservice_id),
    #     'can_done_work': request.user.can_done_work(eservice_id),
    #     'can_add_doers': request.user.is_allowed_group("Керівництво") or request.user.is_allowed_group(
    #         "Загальний відділ") or request.user.is_allowed_group(
    #         "Адміністратори") or request.user.is_manager,
    # }

    # Виставляємо статус "Переглянуто" у листі погоджуючих
    # if request.method == 'POST':
    #     pick_list = json.loads(request.POST.get('selectedList', '[]'))
    #     comment = request.POST.get('pickListComment')
    #     if 'pickListResolution' in request.POST:
    #         res = request.POST.get('pickListResolution')
    #     else:
    #         resolution = None
    #     user_type = request.POST.get('userType')
    #
    #     employee_id_list = []
    #     for id_code in pick_list:
    #         if id_code.startswith('employee_'):
    #             employee_id_list.append(int(id_code.split('_')[1]))

    return views.update(request, eservice_id, created_by_ip, int(step), helper={
        'eservice_permissions': '',
    }, )


def to_approve(request, eservice_id):

    if request.method == 'POST':
        pick_list = json.loads(request.POST.get('selectedList', '[]'))
        comment = request.POST.get('pickListComment')

        user_type = request.POST.get('userType')

        user_id_list = []
        for id_code in pick_list:
            if id_code.startswith('employee_'):
                user_id_list.append(int(id_code.split('_')[1]))

        for user in DeptEmp.objects.filter(user_id__in=user_id_list):
            try:
                obj = EServiceOnApproving.objects.get(eservice_id=eservice_id, assign_to=user.user)
            except EServiceOnApproving.DoesNotExist:
                obj = EServiceOnApproving(eservice_id=eservice_id, assign_to=user.user, created_by=request.user,
                                          created_by_ip=get_ip(request), comment=comment,
                                          submitted=1)
                obj.save()

        eservice = get_object_or_404(EService, pk=eservice_id)
        status = get_object_or_404(EServiceMeta, category_index=3.3)
        eservice.status = status
        eservice.save()
        return redirect('/backend/eservice/' + eservice_id)

    # if "resolutioner" in request.POST:
    #     resolutioner = get_object_or_404(User, pk=request.POST.get("resolutioner"))
    # else:
    #     return HttpResponse(Exception)
    # eserviceOnApproving.objects.create(submitted=True, assign_to=resolutioner, eservice=eservice, )
    # try:
    #     eservice.status = status
    #     eservice.save()
    #
    #     if resolutioner.signed_on_notifications:
    #         send_letter(
    #             "Новий послуга чекає вашої резолюції: {} ({})".format(eservice.internal_id, eservice.title),
    #             'eservice_take_part.email',
    #             {
    #                 'type': "резолюціонером",
    #                 'id': eservice.id,
    #                 'title': eservice.title
    #             },
    #             resolutioner.email
    #         )
    #
    #         # Логуємо
    #         Log(eservice_id=eservice_id, action="послуга було відправлено на резолюцію",
    #             user=request.user).write()
    #         # Виводимо користувачу месседж
    #         messages.success(request, "послугу було відправлено на резолюцію")
    #         return redirect('/backend/eservice/' + eservice_id)
    #     else:
    #         messages.success(request, "послугу було відправлено на резолюцію, врахуйте те що Ваш резолюціонер не підписаний на розсилку повідомлень")
    #         return redirect('/backend/eservice/' + eservice_id)
    # except Exception:
    #     return HttpResponse(Exception)


def to_resolution(request, eservice_id):
    """Відправка на резолюцію

    Args:
        request: об'єкт Django request, eservice_id

    Returns: redirect [object]
    """

    eservice = get_object_or_404(EService, pk=eservice_id)
    status = get_object_or_404(EServiceStatus, pk=3)
    if "resolutioner" in request.POST:
        resolutioner = get_object_or_404(User, pk=request.POST.get("resolutioner"))
    else:
        return HttpResponse(Exception)
    try:
        eservice.resolutioner = resolutioner
        eservice.resolutioner_viewed = False
        eservice.status = status
        eservice.save()
        if resolutioner.signed_on_notifications:
            send_letter(
                "Нова послуга чекає вашої резолюції: {} ({})".format(eservice.internal_id, eservice.title),
                'eservice_take_part.email',
                {
                    'type': "резолюціонером",
                    'id': eservice.id,
                    'title': eservice.title
                },
                resolutioner.email
            )

            # Логуємо
            Log(eservice_id=eservice_id, action="Послугу було відправлено на резолюцію",
                user=request.user).write()
            # Виводимо користувачу месседж
            messages.success(request, "Послугу було відправлено на резолюцію")
            return redirect('/backend/eservice/' + eservice_id)
        else:
            messages.success(request, "Послугу було відправлено на резолюцію, врахуйте те що Ваш резолюціонер не підписаний на розсилку повідомлень")
            return redirect('/backend/eservice/' + eservice_id)
    except Exception:
        return HttpResponse(Exception)


def approve(request, eservice_id):
    """Погодити послугу

    Args:
        request: об'єкт Django request, eservice_id

    Returns: redirect [object]
    """
    eservice = get_object_or_404(EService, id=eservice_id)
    approve_item = \
    EServiceOnApproving.objects.get(eservice_id=eservice_id, assign_to=request.user, submitted=1, done=0)
    status = get_object_or_404(EServiceMeta, category_index=3.4)

    if not approve_item:
        return HttpResponse("Вашого запису про погодження не зайдено")
    else:
        approve_item.done = 1
        approve_item.done_at = datetime.datetime.now()
        if 'comment' in request.POST:
            approve_item.comment = request.POST.get('comment')
        approve_item.save()

        # Перевіряємо че це був останній погодивший. Якщо так - переводимо послугу у статус "Опрацьовано" (13)
        approvers = eservice.eserviceonapproving_set.filter(submitted=1, done=0)
        if approvers:
            messages.success(request, "Ви успішно погодили послугу")
            return redirect('/eservice/{}'.format(eservice.id))
        else:
            if eservice.status.category_index != 3.4:
                eservice.status = status
                # Логуємо
                Log(eservice_id=eservice_id, action="Послугу було переведено у статус 'Опрацьовано'",
                    user=request.user).write()
                messages.success(request, "Послугу погоджено і переведено у статус 'Опрацьовано'")
            else:
                # Логуємо
                Log(eservice_id=eservice_id, action="Послугу було не переведено у статус 'Опрацьовано'",
                    user=request.user).write()
                messages.success(request, "Послугу погоджено і не переведено у статус 'Опрацьовано'")
            eservice.close_at = datetime.datetime.now()
            eservice.save()

            return redirect('/backend/eservice/' + eservice_id)


def reject(request, eservice_id):
    """Відхилення послуги

    Args:
        request: об'єкт Django request, eservice_id

    Returns: redirect [object]
    """

    eservice = get_object_or_404(EService, id=eservice_id)
    status = get_object_or_404(EServiceMeta, category_index=3.2)

    eservice.status = status

    # Логуємо
    Log(eservice_id=eservice_id, action="Послугу було переведено у статус 'Відхилено'",
        user=request.user).write()
    messages.success(request, "Послугу відхилено і переведено у статус 'Відхилено'")

    eservice.save()

    return redirect('/backend/eservice/' + eservice_id)


def eservice_page(request, eservice_id):
    """Картка послуги. Передаємо тип послуги при редагуванні нового послуги
        система автоматично підвантажує обслуговуючий коннектор типу

    Args:
        request: об'єкт Django request, eservice_id

    Returns:
        views.view
    """

    eservice = get_object_or_404(EService, pk=eservice_id)
    type = eservice.type.controller

    views = getattr(__import__(type+'.backend', fromlist=['views']), 'views')
    eservice_permissions = {
        'can_approve': request.user.can_done_approving(eservice_id),
    }
    EServiceOnApproving.objects.filter(assign_to=request.user, eservice=eservice).update(viewed=1,
                                                                                        viewed_at=datetime.datetime.now())
    if eservice.resolutioner == request.user:
        eservice.resolutioner_viewed = True
        eservice.save()
    key_info = get_key_info(request, eservice_id)

    return views.view(request, eservice_id, helper={'eservice_permissions': eservice_permissions, 'key_info': key_info})


def to_edit(request, eservice_id):
    """Повернення послуги на доопрацювання

    Args:
        request: об'єкт Django request, eservice_id

    Returns: redirect [object]
    """

    eservice = get_object_or_404(EService, pk=eservice_id)
    approve_item = EServiceOnApproving.objects.filter(eservice_id=eservice_id, assign_to=request.user, submitted=1, done=0)
    if approve_item:
        status = get_object_or_404(EServiceMeta, category_index=3.5)
        eservice.status = status
        eservice.edit_comment = request.POST.get('editComment')
        eservice.save()
        if eservice.created_by.signed_on_notifications:
            send_letter(
                "Послугу повернуто на доопрацювання {} ({})".format(eservice.internal_id, eservice.title),
                'eservice_take_part.email',
                {
                    'internal_id': eservice.internal_id,
                    'id': eservice.id,
                    'title': eservice.title
                },
                eservice.created_by.email
            )

        Log(eservice_id=eservice_id, action="Послугу повернуто на доопрацювання",
            user=request.user).write()
        messages.success(request, "Послугу було відправлено на доопрацювання")
        return redirect('/backend/eservice/' + eservice_id)
    else:
        return HttpResponseForbidden()
