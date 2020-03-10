# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.urls import path, re_path
from support.backend.views import *
from support.frontend.views import *

urlpatterns = [
    re_path(r'^backend/dialogs-main/$', dialogs, name='dialogs'),
    re_path(r'^dialogs-users/$', dialogs_users, name='dialogs_user'),
    re_path(r'^get-message/$', get_message, name='get_message'),
    re_path(r'^backend/reloadmainchat/$', reloadchatajax, name='reloadmain'),
    re_path(r'^reloaduserchat/$', reloaduserchatajax, name='reloaduser')
]
