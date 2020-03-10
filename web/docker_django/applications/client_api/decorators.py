from django.http import HttpResponse, HttpResponseForbidden
import base64
from client_api.models import ClientApi


def custom_authenticate(func):
    def wrap_function(request, *args, **kwargs):
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                if auth[0].lower() == "basic":
                    uname, passwd = base64.b64decode(auth[1]).decode('utf-8').split(':')
                    try:
                        user = ClientApi.objects.get(login_api=uname, password_api=passwd)
                    except ClientApi.DoesNotExist:
                        user = None
            if user:
                kwargs['user'] = user
                return func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden()
        else:
            return HttpResponseForbidden()
    return wrap_function