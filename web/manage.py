#!/usr/bin/env python
import os
import sys
import multiprocessing as mp
import threading

if __name__ == '__main__':
    basedir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docker_django")
    sys.path.insert(0, basedir)
    sys.path.append(os.path.join(basedir, "modules"))
    sys.path.append(os.path.join(basedir, "applications"))
    sys.path.append(os.path.join(basedir, "eservices"))
    sys.path.append(os.path.join(basedir, "system"))
    # sys.path.insert(0, os.path.join(basedir, "system/cryptography"))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'system.settings.base')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # if sys.argv[1].strip() == "runserver":
    #     d = mp.Process(name='staticCollector', target=lambda: os.system(". /utils/collectstatic-infinite.sh", ))
    #     d.daemon = True
    #     d.start()

    execute_from_command_line(sys.argv)

