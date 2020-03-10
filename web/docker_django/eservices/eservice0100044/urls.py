from django.conf.urls import url, include

from document_66666666666 import views

urlpatterns = [
    url(r'^city_load/$', views.city_load, name='city_load'),

]
