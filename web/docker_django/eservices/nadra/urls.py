from django.conf.urls import url
from django.urls import path

from eservices.nadra import views
from nadra.frontend.views import *

urlpatterns = [
    url(r'^city_load/$', views.city_load, name='city_load'),
    path('areas', views.areas_load, name='areas_load'),
    url(r'^send_to_another/+(?P<eservice_id>[0-9a-zA-Z_]+)$', send_to_another, name='send_to_another'),
    url(r'^step-2/+(?P<eservice_id>[0-9a-zA-Z_]+)$', step_2, name='step_2'),
    url(r'^step-3/+(?P<eservice_id>[0-9a-zA-Z_]+)$', step_3, name='step_3'),
    url(r'^step-4/+(?P<eservice_id>[0-9a-zA-Z_]+)$', step_4, name='step_4'),
    url(r'^step-5/+(?P<eservice_id>[0-9a-zA-Z_]+)$', step_5, name='step_5'),
    url(r'^step-6/+(?P<eservice_id>[0-9a-zA-Z_]+)$', step_6, name='step_6'),

]
