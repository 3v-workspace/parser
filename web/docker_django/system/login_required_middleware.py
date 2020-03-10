from django.http import HttpResponseRedirect

from django.utils.deprecation import MiddlewareMixin
from re import compile

from django.conf import settings

EXEMPT_URLS = [compile(settings.base.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]

class LoginRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, 'user')
        if not request.user.is_authenticated:
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in EXEMPT_URLS):
                return HttpResponseRedirect(settings.LOGIN_URL)