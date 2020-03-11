import django

from system import settings

if "mailer" in settings.base.INSTALLED_APPS:
    from mailer import send_html_mail
else:
    from django.core.mail import send_mail
from django.template.loader import render_to_string

from system.settings.base import DEFAULT_FROM_EMAIL


def send_letter(subject, template_name, context, email):
    template_html = render_to_string('emails/' + template_name, context)
    if not type(email) is list:
        email = [email]

    send_html_mail(
        subject,
        template_html,
        template_html,
        DEFAULT_FROM_EMAIL,
        email,
        # message_html=template_html,
    )

