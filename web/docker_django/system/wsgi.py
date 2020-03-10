"""
WSGI config for system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'system.settings.base')

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(basedir, "modules"))
sys.path.append(os.path.join(basedir, "applications"))
sys.path.append(os.path.join(basedir, "eservices"))

application = get_wsgi_application()
