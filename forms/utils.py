from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.core.mail import get_connection


def send_mail(subject, message, recipient_list, from_email=None, **kwargs):
    """
    Modified clone of wagtail.admin.utils.send_mail that omits the
    'Auto-Submitted: auto-generated' header

    This is motivated by the fact that Redmine discards messages containing
    that header and we use FormPage emails to auto-create Redmine tickets

    See: https://github.com/freedomofpress/infrastructure/issues/1982
    """

    if not from_email:
        if hasattr(settings, 'WAGTAILADMIN_NOTIFICATION_FROM_EMAIL'):
            from_email = settings.WAGTAILADMIN_NOTIFICATION_FROM_EMAIL
        elif hasattr(settings, 'DEFAULT_FROM_EMAIL'):
            from_email = settings.DEFAULT_FROM_EMAIL
        else:
            from_email = 'webmaster@localhost'

    connection = kwargs.get('connection', False) or get_connection(
        username=kwargs.get('auth_user', None),
        password=kwargs.get('auth_password', None),
        fail_silently=kwargs.get('fail_silently', None),
    )
    multi_alt_kwargs = {'connection': connection}
    mail = EmailMultiAlternatives(subject, message, from_email, recipient_list, **multi_alt_kwargs)
    html_message = kwargs.get('html_message', None)
    if html_message:
        mail.attach_alternative(html_message, 'text/html')

    return mail.send()
