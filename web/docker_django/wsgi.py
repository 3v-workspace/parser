"""
WSGI config for system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application

basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(basedir, "modules"))
sys.path.append(os.path.join(basedir, "applications"))
sys.path.append(os.path.join(basedir, "eservices"))
sys.path.append(os.path.join(basedir, "system"))
sys.path.append(basedir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'system.settings.base')

application = get_wsgi_application()