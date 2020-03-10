from threading import local

from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import resolve
my_local_global = local()


class UserGroupPermission(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            app_name = resolve(request.path).app_name
            if 'backend' == app_name or 'backend_reports' == app_name:
                try:
                    group_operators = Group.objects.get(name='Оператори')
                    group_leaders = Group.objects.get(name='Керівники')
                    if group_operators not in request.user.groups.all() and group_leaders not in request.user.groups.all():
                        return HttpResponseForbidden()
                except:
                    return HttpResponseForbidden()

        return self.get_response(request)

    def process_request(self, request):
        pass


class IsAccessGroup(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.user.group_permissions = True

            try:
                group_operators = Group.objects.get(name='Оператори')
                group_leaders = Group.objects.get(name='Керівники')
                if group_operators not in request.user.groups.all() and group_leaders not in request.user.groups.all():
                    request.user.group_permissions = False
                    # return request.user.group_permissions
            except:
                request.user.group_permissions = False
                # return request.user.group_permissions

        return self.get_response(request)

    def process_request(self, request):
        pass


class UserLegalMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:

            request.user.is_legal = True if request.user.type == 'legal' else False

        return self.get_response(request)

    def process_request(self, request):
        pass



# #login required
# EXEMPT_URLS = [compile(settings.base.LOGIN_URL.lstrip('/'))]
# if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
#     EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]
#
# class LoginRequiredMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         assert hasattr(request, 'user')
#         if not request.user.is_authenticated:
#             path = request.path_info.lstrip('/')
#             if not any(m.match(path) for m in EXEMPT_URLS):
#                 return HttpResponseRedirect