from os import path
from django.template.loader import render_to_string

from system.settings.base import INSTALLED_APPS

if "mailer" in INSTALLED_APPS:
    from mailer import send_html_mail
else:
    from django.core.mail import send_mail
from django.template.loader import render_to_string


BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))


def send_letter(subject, template_name, context, email):
    template_html = render_to_string('emails/' + template_name, context)
    if not type(email) is list:
        email = [email]

    # send_html_mail(
    #     subject,
    #     template_html,
    #     template_html,
    #     DEFAULT_FROM_EMAIL,
    #     email,
    #     # message_html=template_html,
    # )


def get_path(dir):
    '''
    Повертає системний шлях до вказаної теки

    Args:
        dir: Назва чи шлях теки від корня проекту

    Returns:
        str: Системний шлях
    '''
    dir_path = path.join(BASE_DIR, dir)
    return dir_path

def is_file_exists(dir, filename):
    '''
    Повертає True якщо файл у заданій директорії існує, або False якщо ні
    Args:
        filename: назва файлу з розширенням

    Returns:
        Bool
    '''

    exists = path.exists(get_path(dir)+filename)
    return exists
