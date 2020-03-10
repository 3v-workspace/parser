"""Celery init."""
from __future__ import absolute_import, unicode_literals

import os
import importlib

from celery import Celery
# set the default Django settings module for the 'celery' program.
import sys
import os

basedir = "/app/docker_django"
sys.path.insert(0, basedir)
sys.path.append(os.path.join(basedir, "modules"))
sys.path.append(os.path.join(basedir, "applications"))
sys.path.append(os.path.join(basedir, "eservices"))
sys.path.append(os.path.join(basedir, "system"))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'system.settings.base')

from django.conf import settings

app = Celery("system")
app.config_from_object("django.conf:settings", namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)