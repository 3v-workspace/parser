import json
import requests
from Crypto.Hash import SHA
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from authorization.config import CLIENT_CREDENTIALS, IP_PORTS
from authorization.models import UserTemporaryCode
from authorization.services import AuthService
from stronghold.decorators import public
from system.email_sender import send_letter


def logout_function(request):
    logout(request)
    return redirect('/')




@csrf_exempt
@public
def get_token_by_code(request):
    """Отримання токена користувача за кодом.
    Для отримання даних про користувача, який в процесі реєстрації.

    Args:
        request: об'єкт Django request.

    Returns:
        JSON об'єкт з полем token - токен автентифікації користувача в РМ.
    """
    code = request.GET.get('code')
    token = UserTemporaryCode.objects.filter(code=code).first()
    if token:
        key = token.user.auth_token.key
        token.delete()
        return HttpResponse(json.dumps({'token': key}))
    return HttpResponse(status=404)
