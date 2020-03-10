from django.conf.urls import url, include

from eservice0100043 import views

urlpatterns = [
    url(r'^city_load/$', views.city_load, name='city_load'),

]
