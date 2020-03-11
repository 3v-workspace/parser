# Celery settings
from __future__ import absolute_import, unicode_literals

from celery.schedules import crontab, timedelta
from .base import USE_TZ, TIME_ZONE
# USE_TZ = False
# TIME_ZONE = "Europe/Kiev"

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#time-zones
if USE_TZ:
    CELERY_ENABLE_UTC = True
    CELERY_TIMEZONE = TIME_ZONE

# Enables error emails.
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_DISABLE_RATE_LIMITS = True
CELERY_WORKER_DISABLE_RATE_LIMITS = CELERY_DISABLE_RATE_LIMITS
# https://khashtamov.com/2016/02/celery-best-practices/

# http://www.rkblog.rk.edu.pl/w/p/using-sentry-log-exceptions-and-logging-messages-django-projects/
CELERYD_HIJACK_ROOT_LOGGER = False
CELERY_WORKER_HIJACK_ROOT_LOGGER = CELERYD_HIJACK_ROOT_LOGGER

# if you want to place the schedule file relative to your project or something:
# CELERYBEAT_SCHEDULE_FILENAME = "some/path/and/celerybeat-schedule"

CELERY_BEAT_SCHEDULE = {
    "permissions-updater": {
        "task": "eservice.tasks.check_permission_expiration",
        "schedule": crontab(hour="0", minute="1"),
    }
    # "map_updater": {
    #     "task": ".tasks.map_updater",
    #     "schedule": crontab(hour=23, minute=59),
    # },
}

# CELERY_RE = 'amqp://admin:admin@rabbitmq:5672//'
CELERY_BROKER_URL = 'amqp://admin:admin@rabbitmq:5672//'
# CELERY_RESULT_BACKEND = "redis://redis:6379/2"
# CELERY_BROKER_URL = "redis://redis:6379/2"