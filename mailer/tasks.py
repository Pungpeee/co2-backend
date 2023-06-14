import logging

from django.conf import settings

from config.models import Config
from .models import Mailer

logger = logging.getLogger('mailtask')


def send_mail(to, subject, body, types):
    if not Config.pull_value('config-mailer-is-enable'):
        return
    if type(to) is list:
        for email in to:
            mailer = Mailer.objects.create(to=email, subject=subject, body=body, type=types)
            task_send_mail_use_service(mailer.id)
    else:
        mailer = Mailer.objects.create(to=to, subject=subject, body=body, type=types)
        task_send_mail_use_service(mailer.id)


def task_send_mail_use_service(mailer_id):
    mailer = Mailer.objects.filter(id=mailer_id).first()
    # _service = mailer.settings['service']
    _service = 'DJANGO'
    if _service == 'DJANGO':
        mailer.send_django()
    elif _service == 'SMTP':
        mailer.send_smtp()
    elif _service == 'MAILGUN':
        mailer.send_mailgun()
    else:
        mailer.send_django()
        logger.warning('Unknown SMTP Host')
