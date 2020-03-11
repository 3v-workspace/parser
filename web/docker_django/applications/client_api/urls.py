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

from applications.client_api import views

urlpatterns = [
    url(r'^load_field/(?P<eservice_id>[0-9]+)', views.admin_change_field, name='admin_change_field'),

    url(r'^(?P<eservice_type>.*)/(?P<inn>[0-9]+)/list', views.eservice_list, name='eservice_list'),
    url(r'^(?P<eservice_type>.*)/(?P<inn>[0-9]+)/card/(?P<card_id>[0-9]+)', views.eservice_card,
        name='eservice_card'),


]