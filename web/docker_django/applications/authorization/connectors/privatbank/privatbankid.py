import json
import requests

from django.shortcuts import redirect
from django.urls import reverse
from Crypto.Hash import SHA
from django.contrib.auth import login, logout
from stronghold.decorators import public
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseRedirect

from authorization.services import AuthService


@public
def bank_id_log_in(request):
    """Логін через банк в BankId.

    Args:
        request: об'єкт Django request.

    Returns:
        Перенаправляє на сторінку логіну через банк в BankID, звідки іде перенаправлення на
         функцію реєстрації в системі РМ.
    """

    redirect_uri = reverse('bank_id_auth')
    full_uri = request.build_absolute_uri(redirect_uri)
    source_origin = request.GET.get('origin', '')
    full_uri += '?origin={0}'.format(source_origin)
    return redirect('https://bankid.privatbank.ua/DataAccessService/das/authorize?response_type=code&' +
                    'client_id={1}&redirect_uri={0}'.format(full_uri, settings.PRIVATBANKID_CLIENT_ID))


@public
def bank_id_auth(request):
    """Отримання даних про користувача та реєстрація його в системі.

    Дані отримуються з системи BankID.

    Args:
        request: об'єкт Django request.

    Returns:
        Перенаправлення на сторінку заповнення даних про користувача.

    """
    service = AuthService()
    ip_port = settings.PRIVATBANKID_AUTH_DOMAIN
    redirect_uri = reverse('bank_id_auth')
    full_uri = request.build_absolute_uri(redirect_uri)
    source_origin = request.GET.get('origin', '')
    full_uri += '?origin={0}'.format(source_origin)
    code = request.GET.get('code')
    client_secret = SHA.new(bytes(
        settings.PRIVATBANKID_CLIENT_ID+settings.PRIVATBANKID_SECRET+code, 'utf-8'
    )).hexdigest()
    r = requests.get(
        '{0}/DataAccessService/oauth/token?grant_type=authorization_code&'
        'client_id={1}&client_secret={2}&code={3}&redirect_uri={4}'.format(
            ip_port, settings.PRIVATBANKID_CLIENT_ID, client_secret, code, full_uri))
    response = r.json()

    request_url = "{0}/ResourceService/checked/data".format(ip_port)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {access_token},Id {client_id}'.format(access_token=response['access_token'],
                                                                       client_id=settings.PRIVATBANKID_CLIENT_ID),
        'Accept': 'application/json'
    }
    data = {
        "type": "physical",
        "fields":
            ["firstName", "middleName", "lastName", "phone", "inn", "email",],
        "addresses": [
            {"type": "factual",
             "fields": ["state"]}],
    }
    post_r = requests.post(request_url, data=json.dumps(data), headers=headers)
    post_response = post_r.json()

    if post_response.get('customer', False):

        if not post_response['customer'].get('edrpou', False) and not post_response['customer'].get('inn', False):
            messages.add_message(request, messages.ERROR,
                                 'Нажаль обраний вами спосіб аутентифікації не надав нам код ІНН або код ЄДРПОУ, '
                                 'тому ми не можемо впустити вас у систему')
            return HttpResponseRedirect('/accounts/login/', messages)

        if post_response['customer'].get('inn', False) and not (post_response['customer'].get('edrpou', False)):
            if not (post_response['customer'].get('lastName', False)) and not (
            post_response['customer'].get('firstName', False)) \
                    and not (post_response['customer'].get('middleName', False)):
                messages.add_message(request, messages.ERROR,
                                     'Нажаль обраний вами спосіб аутентифікації не надав нам ПІБ, '
                                     'тому ми не можемо впустити вас у систему')
                return HttpResponseRedirect('/accounts/login/', messages)

        if not post_response['customer'].get('signature', False):
            messages.add_message(request, messages.ERROR,
                                 'Внутрішня помилка сервісу автентифікації')
            return HttpResponseRedirect('/accounts/login/', messages)

    if post_response['state'] == 'ok' and post_response.get('customer', False):
        signature, customer_type = post_response['customer'].pop('signature'), post_response['customer'].pop('type',
                                                                                                             None)
        addresses = post_response['customer'].pop('addresses', None)
        post_response_customer = post_response['customer']

        if addresses[0].get('state', False):
            post_response_customer['state'] = addresses[0]['state']

        user = service.authenticate(encrypted_data=post_response_customer, signature=signature, source='privatbank')

        if user.get('user', False):
            login(request, user['user'], backend='django.contrib.auth.backends.ModelBackend')

            if not request.user.is_active:
                logout(request)
    else:
        if post_response.get('desc', False):
            messages.add_message(request, messages.ERROR,
                                 'Виникла помилка при спробі автентифікації' + ' - ' + post_response.get('desc', False))
            return HttpResponseRedirect('/accounts/login/', messages)
    return redirect('/')