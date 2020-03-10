import json
import requests
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from authorization.services import AuthService
from stronghold.decorators import public
from django.conf import settings

from authorization.connectors.id_gov_ua.auth_settings import CLIENT_CREDENTIALS
from system.email_sender import send_letter



@public
def gov_ua_log_in(request):
    """Логін через банк в BankId.

    Args:
        request: об'єкт Django request.

    Returns:
        Перенаправляє на сторінку логіну через банк в BankID, звідки іде перенаправлення на
         функцію реєстрації в системі РМ.
    """
    full_uri = settings.SITE_URL + '/auth/auth'
    return redirect('https://id.gov.ua/?response_type=code&' +
                    'client_id={1}&redirect_uri={0}'.format(full_uri, CLIENT_CREDENTIALS['ID']))


@public
def gov_ua_auth(request):
    """Отримання даних про користувача та реєстрація його в системі.

    Дані отримуються з системи.

    Args:
        request: об'єкт Django request.

    Returns:
        Перенаправлення на сторінку заповнення даних про користувача.

    """
    service = AuthService()
    redirect_uri = reverse('gov_ua_auth')
    # full_uri = request.build_absolute_uri(redirect_uri)
    full_uri = settings.SITE_URL + '/auth/auth'
    source_origin = request.GET.get('origin', '')
    code = request.GET.get('code')

    try:
        r = requests.post('https://id.gov.ua/get-access-token', data={"grant_type": 'authorization_code',
                                                                      "client_id": CLIENT_CREDENTIALS['ID'],
                                                                      "client_secret": CLIENT_CREDENTIALS['SECRET'],
                                                                      "code": code,
                                                                      "redirect_uri": full_uri, })
        response = r.json()
    except:
        messages.add_message(request, messages.ERROR,
                             'Внутрішня помилка серверу аутентифікації ID.ORG.UA. Спробуйте пізніше або виберіть '
                             'інший спосіб '
                             'аутентифікацї')
        return HttpResponseRedirect('/accounts/login/', messages)

    if not response.get('access_token', None) and not response.get('user_id', None):
        messages.add_message(request, messages.ERROR,
                             'Внутрішня помилка серверу аутентифікації ID.ORG.UA. Спробуйте вибрати інший спосіб '
                             'аутентифікацї')
        return HttpResponseRedirect('/accounts/login/', messages)
    else:
        data_r = requests.get(
            'https://id.gov.ua/get-user-info?access_token={0}&user_id={1}'.format(response['access_token'],
                                                                                  response['user_id']))

    try:
        data_response = data_r.json()
    except:
        messages.add_message(request, messages.ERROR,
                             'Нажаль обраний вами спосіб аутентифікації не надав нам код ІНН, тому ми не можемо '
                             'впустити вас у систему')
        data_r_email = str(data_r)
        send_letter('Кабінет водія. Помилка', 'login_error.email',
                    {'data_response': data_r_email, 'domain': settings.SITE_URL},
                    ['lily.bevcuk@gmail.com',])
        return HttpResponseRedirect('/accounts/login/', messages)

    if not (data_response.get('drfocode', None)) and not (data_response.get('edrpoucode', None)):
        messages.add_message(request, messages.ERROR,
                             'Нажаль обраний вами спосіб аутентифікації не надав нам код ІНН або код ЄДРПОУ, '
                             'тому ми не можемо впустити вас у систему')
        return HttpResponseRedirect('/accounts/login/', messages)

    if data_response.get('drfocode', None) and not (data_response.get('edrpoucode', None)):
        if not (data_response.get('lastname', None)) and not (data_response.get('givenname', None)) \
                and not (data_response.get('middlename', None)):
            messages.add_message(request, messages.ERROR,
                                 'Нажаль обраний вами спосіб аутентифікації не надав нам ПІБ, '
                                 'тому ми не можемо впустити вас у систему')
            return HttpResponseRedirect('/accounts/login/', messages)

    # try:

    user_code = service.authenticate(encrypted_data=data_response, source='id_gov_ua')

    if user_code.get('user', False):
        login(request, user_code['user'], backend='django.contrib.auth.backends.ModelBackend')

        if not request.user.is_active:
            logout(request)

        return redirect('/')

    # except Exception as e:
    #     data_response_email = str(data_response)
    #     send_letter('Помилка', 'login_error.email',
    #                 {'data_response': data_response_email, 'domain': SITE_URL},
    #                 ['lily.bevcuk@gmail.com',])
    #     messages.error(request,
    #                    'Помилка сервісу аутентифікації ID.ORG.UA. Спробуйте пізніше або виберіть інший спосіб '
    #                    'аутентифікації на сайті сервісу')
    #     return HttpResponseRedirect('/accounts/login/', messages)

    return redirect('/')
