from django.conf import settings
from django.db import models

from config.models import Config


class Mailer(models.Model):
    STATUS_CHOICES = (
        (0, 'FAILED'),
        (1, 'WAITING'),
        (2, 'SUCCESS'),
    )

    TYPE_CHOICES = (
        (1, 'Reset Password'),
        (2, 'Inbox'),
        (4, 'Notify'),
        (5, 'Contact')
    )

    inbox = models.ForeignKey('inbox.Inbox', related_name='+', blank=True, null=True, on_delete=models.CASCADE)
    to = models.CharField(max_length=255, blank=True, null=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    type = models.IntegerField(choices=TYPE_CHOICES, default=0)
    attach_file = models.FileField(upload_to='attach_file/%Y/%m/', null=True)

    payload = models.TextField(blank=True, null=True, default='')
    traceback = models.TextField(blank=True, null=True, default='')

    datetime_send = models.DateTimeField(blank=True, null=True, db_index=True)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True)

    class Meta:
        default_permissions = ()
        ordering = ['-datetime_create']

    @property
    def status_label(self):
        return self.get_status_display()

    @property
    def type_label(self):
        return self.get_type_display()

    @property
    def settings(self):
        from config.models import Config
        return Config.pull_value('notification-email-list')

    @staticmethod
    def push_and_send(subject, body, account, attachment=None):
        if not Config.pull_value('config-mailer-is-enable') or settings.IS_LOCALHOST:
            return
        mailer = Mailer.objects.create(
            to=account.email,
            subject=subject,
            body=body,
            type=2,  # inbox type
        )

        if not settings.TESTING:
            if attachment:
                mailer.attach_file.save('invite.ics', attachment)

            mailer.send()

    def send(self):
        from config.models import Config
        from django.core.validators import validate_email, ValidationError
        config = Config.pull_value('notification-email-list')
        service = config['service']
        try:
            validate_email(self.to)
        except ValidationError:
            self.status = 0
            self.save(update_fields=['status', 'datetime_update'])
            return
        try:
            if service == 'DJANGO':
                self.send_django()
            elif service == 'MAILGUN':
                self.send_mailgun()
        except Exception as error:
            self.traceback = error
            self.status = 0
            self.save(update_fields=['status', 'traceback'])
            print('%s \n' % error)

    def send_smtp(self, recipients=None):
        import smtplib
        import traceback
        import logging

        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.utils import formataddr
        from email.mime.base import MIMEBase
        from email import encoders
        from django.utils import timezone
        from django.conf import settings
        from config.models import Config
        from socket import gaierror, timeout

        logger = logging.getLogger('SMTP')
        _settings = self.settings['settings']
        try:
            msg = MIMEMultipart()
            from_address = Config.pull_value('mailer-from-email')

            if from_address in ['', None]:
                from_address = _settings['EMAIL_HOST_USER']
            if 'EMAIL_HOST_ALIAS' in _settings:
                if _settings['EMAIL_HOST_ALIAS']:
                    msg['From'] = formataddr((_settings['EMAIL_HOST_ALIAS'], from_address))
                else:
                    msg['From'] = from_address

            if recipients:
                msg['To'] = ', '.join(recipients)
                email = recipients
            else:

                msg['To'] = self.to
                email = self.to

            msg['Subject'] = self.subject
            msg.attach(MIMEText(self.body, 'html'))

            if self.attach_file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(self.attach_file.read())
                encoders.encode_base64(part)
                if '.ics' in self.attach_file.name:
                    filename = 'invite.ics'
                else:
                    filename = self.attach_file.name.rsplit('/', 1)[1]
                part.add_header(
                    'Content-Disposition',
                    'attachment; filename=%s' % filename
                )
                msg.attach(part)


            if _settings['EMAIL_PORT'] == 25 and not _settings.get('EMAIL_USE_AUTH', False):  # AIS
                if Config.pull_value('mailer-is-replace-domain'):  # Stg
                    _ = Config.pull_value('mailer-replace-domain').split(',')
                    a = _[0].strip()
                    b = _[1].strip()
                    email = email.replace(a, b)
                try:
                    server = smtplib.SMTP(host=_settings['EMAIL_HOST'], port=25, timeout=settings.DEFAULT_TIMEOUT)
                except (gaierror, timeout, smtplib.SMTPConnectError) as e:
                    logger.error(e)
                    raise smtplib.SMTPException

                server.set_debuglevel(1)
                server.sendmail(from_address, email, msg.as_string())
                server.quit()
            else:
                try:
                    server = smtplib.SMTP(_settings['EMAIL_HOST'], _settings['EMAIL_PORT'],
                                          timeout=settings.DEFAULT_TIMEOUT)
                except (gaierror, timeout, smtplib.SMTPConnectError) as e:
                    logger.error(e)
                    raise smtplib.SMTPException

                server.ehlo()
                is_tls = _settings['EMAIL_USE_TLS'] if 'EMAIL_USE_TLS' in _settings else True
                if is_tls:
                    server.starttls()
                    server.ehlo()
                is_auth = _settings['EMAIL_USE_AUTH'] if 'EMAIL_USE_AUTH' in _settings else True
                if is_auth:
                    server.login(_settings['EMAIL_HOST_USER'], _settings['EMAIL_HOST_PASSWORD'])
                server.sendmail(from_address, email, msg.as_string())
                server.quit()

            if not self.to:
                self.to = msg['to']
                self.save(update_fields=['to'])

            self.datetime_send = timezone.now()
            self.status = 2
            self.save(update_fields=['status', 'datetime_send'])
        except:
            self.traceback = traceback.format_exc()
            self.status = 0
            self.save(update_fields=['status', 'traceback'])

    def send_django(self, recipients=None):
        import smtplib
        import traceback

        from django.core.mail import send_mail
        from django.utils import timezone

        _settings = self.settings
        if recipients is None:
            if not self.to:
                email = ''
            else:
                email = self.to
        else:
            email = recipients
        try:
            send_mail(subject=self.subject,
                      message='',
                      from_email=_settings['settings']['EMAIL_HOST_USER'],
                      recipient_list=[email],
                      html_message=self.body)
            self.datetime_send = timezone.now()
            self.status = 2
            self.save()
        except smtplib.SMTPException:
            self.traceback = traceback.format_exc()
            self.status = 0
            self.save()

    def send_mailgun(self):
        import requests
        import ast
        from config.models import Config
        mail_gun_config = Config.pull('config-mailer-mailgun-token')
        mail_gun_config = mail_gun_config.value
        if isinstance(mail_gun_config, str):
            mail_gun_config = ast.literal_eval(mail_gun_config)
        if not mail_gun_config['site']:
            self.status = 0
            self.save()
        else:
            site_format_json = {
                'site': mail_gun_config['site'],
                'param': 'messages'
            }
            site = '{site}/{param}'.format(**site_format_json)
            files = {}
            if self.attach_file:
                files = {
                    'attachment': open(self.attach_file, 'rb')
                }

            response = requests.post(
                site,
                auth=(
                    'api', mail_gun_config['key']
                ),
                data={
                    'from': mail_gun_config['from'],
                    'to': [self.to],
                    'subject': self.subject,
                    'text': self.body
                },
                files=files
            )
            if response.status_code == 200 or response.status_code == 201:
                self.status = 2
            else:
                self.status = 0
            self.traceback = response.text
            self.save()


class Template(models.Model):
    subject = models.CharField(max_length=120)
    body = models.TextField()

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True)

    class Meta:
        default_permissions = ()
