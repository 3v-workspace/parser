import base64

from Crypto.Cipher import PKCS1_v1_5
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from ipware.ip import get_ip

from eservice.models import EService, Log
from eservice.forms import DocumentStarForm
from eservice.models import EServiceStar
from eservice.models import EServiceSign
from django.conf import settings

User = get_user_model()


def eservice_create(request):
    """Створення послуги.

    Args:
        request: об'єкт Django request

    Returns: render
    """

    return render(request, "eservice/eservices_list.html", {})


def estimation_service(request, eservice_id):
    """Оцінка послуги.

    Args:
        request: об"єкт Django request, eservice_id

    Returns: JsonResponse
    """

    if request.method == "POST":
        form = DocumentStarForm(request.POST)
        if form.is_valid():
            eservice_star = form.save(commit=False)
            eservice_star.created_by_id = request.user.id
            eservice_star.eservice_id = eservice_id

            quality = form.cleaned_data["quality"] or 0
            easy_ordering = form.cleaned_data["easy_ordering"] or 0
            term_service = form.cleaned_data["term_service"] or 0

            if (quality + easy_ordering + term_service) != 0:
                eservice_star.average_value = "{:.1f}".format((quality + easy_ordering + term_service) / 3)
            else:
                eservice_star.average_value = 0

            eservice_star.save()

            e_services = EService.objects.filter(created_by=request.user).distinct()
            exist_estimation = EServiceStar.objects.filter(eservice_id=eservice_id, created_by=request.user)

            refresh_html = render_to_string("eservice/refresh_estimation.html",
                                            {"exist_estimation": exist_estimation, "e_services": e_services}, request=request)

            return JsonResponse({
                "refresh_html": refresh_html,
            })

    return render(request, "eservice/eservices_list.html", {})


def my_eservices(request):
    '''

    Returns: redirect [object]
    '''

    my_eservices = EService.objects.filter(created_by=request.user).distinct()
    form = DocumentStarForm()
    return render(request, "eservice/my_eservices.html", {"my_eservices": my_eservices, "form": form})


# Таким чином передаємо тип послуги при створенні нового послуги
# система автоматично підвантажує обслуговуючий коннектор типу
def create_eservice(request, eservice_type,):

    views = getattr(__import__(eservice_type+".frontend", fromlist=["views"]), "views")
    created_by_ip = get_ip(request)
    return views.create(request, created_by_ip,)


# Картка послуги
def eservice_page_front(request, eservice_id):

    e_service = get_object_or_404(EService, pk=eservice_id)
    type = e_service.type.controller

    views = getattr(__import__(type+".frontend", fromlist=["views"]), "views")
    e_service_permissions = {
        "can_approve": request.user.can_done_approving(eservice_id),
    }
    return views.view(request, eservice_id, helper={"e_service_permissions": e_service_permissions})


def another_sign(request, encoded):

    from crypto_info.views import decrypt_public_key
    private = PRIVATE_KEY_SIGN
    decrupt_base64_dict = decrypt_public_key(encoded.encode('utf-8'), private)

    my_dict_again = eval(base64.b64decode(decrupt_base64_dict))

    eservice_id = my_dict_again['eservice_id']
    user_id = my_dict_again['id']

    e_service = get_object_or_404(EService, pk=eservice_id)
    created = get_object_or_404(User, pk=user_id)
    sign_email = my_dict_again['email']
    if sign_email != request.user.email:
        messages.add_message(request, messages.ERROR,
                             'Ваш емейл не співпадає з тим який був вказаний для підпису')
    else:
        EServiceSign.objects.get_or_create(eservice=e_service, user=request.user)

    return redirect('/eservice/' + str(e_service.id))


def eservice_signature(request, eservice_id):
    e_service = get_object_or_404(EService, pk=eservice_id)
    return render(request, "eservice0100043/frontend/create_step_2.html", {
        "id_test_service": e_service.id,
        "eservice_type": e_service.type.model,
        "apps": e_service.type.controller,
    })