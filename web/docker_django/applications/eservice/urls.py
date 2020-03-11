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
from django.conf.urls import url, include

from eservice import views

urlpatterns = [
    url(r'^create/$', views.eservice_create, name='eservice_create'),
    url(r'^my_eservices/$', views.my_eservices, name='my_eservices'),
    url(r'^create/+(?P<eservice_type>[0-9a-zA-Z_]+)', views.create_eservice,
        name='create_eservice'),
    url(r'^create/$', views.eservice_create, name='eservice_create'),
    url(r'^estimation_service/+(?P<eservice_id>[0-9a-zA-Z_]+)$', views.estimation_service, name='estimation_service'),

    url(r'^another_sign/+(?P<encoded>.*)/', views.another_sign, name='another_sign'),
    url(r'^eservice_signature/+(?P<eservice_id>[0-9a-zA-Z_]+)$', views.eservice_signature, name='eservice_signature'),
    url(r'^(?P<eservice_id>[0-9]+)', views.eservice_page_front, name='eservice_page'),

]