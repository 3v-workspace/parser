"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from decorator_include import decorator_include
from django.conf.urls import url, include, re_path
from django.contrib import admin
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.http.response import HttpResponse
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

from system import views

# urlpatterns = i18n_patterns(
from system.decorators import group_required

urlpatterns = [
    path('_admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r"^robots\.txt$", csrf_exempt(views.robots), name="robots_file"),
    url(r'^auth/', include('authorization.urls'), name='auth'),  # авторизація
    url(r'accounts/login/$', views.return_reg_template, name='login'),
    url(r'^sign/', include('signature.urls'), name='sign'),
    url(r'^eservice/', include('eservice.urls')),
    url(r'^eservice0100043/', include('eservice0100043.urls')),
    url(r'^eservice/nadra/', include('eservices.nadra.urls')),
    url(r'^client_api/', include('client_api.urls')),

    path('backend/', decorator_include(group_required(['Оператори', 'Керівники']), 'backend.urls')),

    url(r'^backend/reports/', include('reports.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^', include('support.urls')),
    url(r'^nested_admin/', include('nested_admin.urls')),
    # url(r'^report_builder/', include('report_builder.urls')),
    re_path(r'^elements/',  views.elements, name='elements'),
    re_path(r'^documentation/',  views.documentation, name='documentation'),
    re_path(r'^trembita/', include('modules.trembita.urls')),
    re_path(r'^sev/', include('modules.sev_ovv.urls')),
    re_path(r'infinitive/$', views.infinitive, name='infinitive'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
