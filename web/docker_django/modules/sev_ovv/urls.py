"""Головний файл url для SEV OVV"""
from django.conf.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^sev/', views.sev),
]