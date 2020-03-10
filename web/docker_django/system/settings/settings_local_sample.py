SITE_ID = 1
SECRET_KEY = 'qus+h6pl%n76&_1mq38twueoghlDJKSVUIjaw35434qfaw080ig='  # change the secret key for your local system.

# Debug mode options
DEBUG = True

# SECURITY WARNING: don't run with debug turned on in production!
if (DEBUG):
    ALLOWED_HOSTS = ["*"]
    # ALLOWED_HOSTS = ['127.0.0.1', "localhost"]
    INTERNAL_IPS = ['192.168.1.8', '127.0.0.1']
else:
    ALLOWED_HOSTS = ['*']
    INTERNAL_IPS = ['*']# Static folder definations:


# Please, change the admin name and email for your own. This is used for error-log sending
ADMINS = (
    ('Admin', 'ugin.email@gmail.com'),
)
MANAGERS = ADMINS

# Please, choose propriate email backend for your own goals. For develop and testing use console email backend only.
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # CONSOLE MODE - for development purposes.
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  #SMTP - for production server.
EMAIL_BACKEND = 'mailer.backend.DbBackend'

# SMTP settings
EMAIL_USE_SSL = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'project@gmail.com'
EMAIL_HOST_PASSWORD = 'Forev'
DEFAULT_FROM_EMAIL = 'Назва проекту <project@gmail.com>'
DEFAULT_TO_EMAIL = 'project@gmail.com'
TIMEOUT = 1