import functools

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseForbidden


def group_required(group_name):
    def decorator(view):
        @functools.wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.user.groups.filter(name__in=group_name):
                return view(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("У вас нема доступу до даної сторінки")
        return wrapper
    return decorator
