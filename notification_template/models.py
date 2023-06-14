from django.utils import timezone

from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.template.loader import render_to_string

from mailer.models import Mailer
from utils.model_permission import DEFAULT_PERMISSIONS


class Trigger(models.Model):
    NOTIFICATION_CHOICE = (
        (0, 'both'),
        (1, 'mail'),
        (2, 'notification'),
    )

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, db_index=True)
    available_condition = models.TextField(blank=True, null=True)
    available_correspond = models.TextField(blank=True, null=True)
    available_param = models.TextField()
    available_subject = models.TextField(blank=True, null=True)
    available_body = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    action = models.IntegerField(choices=NOTIFICATION_CHOICE, default=0)
    current_template = models.ForeignKey('notification_template.Template', on_delete=models.CASCADE)

    account_update = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+', on_delete=models.CASCADE)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True)

    class Meta:
        default_permissions = DEFAULT_PERMISSIONS
        ordering = ['id']

    def __str__(self):
        return self.name

    @staticmethod
    def get_code(code):
        from .init_data import CONFIG_DICT
        # Config dict made for set mail template from outside when init file fail
        trigger = Trigger.objects.filter(code=code).first()
        if trigger is None and code in CONFIG_DICT:
            template = Template.objects.create(
                is_standard=True,
                subject=CONFIG_DICT[code]['subject'],
                body=CONFIG_DICT[code]['body'],
                event_trigger=None
            )
            trigger = Trigger.objects.create(
                name=code,
                code=code,
                available_param=CONFIG_DICT[code]['available_param'],
                current_template=template
            )
            template.event_trigger = trigger
            template.save()
        return trigger

    def send_notification(self,
                          sender=None,
                          inbox_type=None,
                          inbox_content_type=None,
                          inbox_content_id=None,
                          account_list=[],
                          ):
        from inbox.models import Inbox
        from .utils_templates import get_data
        from account.models import Account

        if not self.is_active or not account_list:
            return

        template = self.current_template
        account = None
        for account_id in account_list:
            if account_id is not None:
                if isinstance(account_id, int):
                    account = Account.pull(account_id)
                elif isinstance(account_id, dict):
                    account = Account.pull(account_id)
                elif isinstance(account_id, Account):
                    account = Account.pull(account_id.id)

            if not account:
                return

            # case check in complete and check in fail
            payload = get_data(self.code, account, inbox_content_type, inbox_content_id)
            '''
                close for manage less template (Not solid design)
            '''
            # mail_subject = ''
            # mail_body = ''
            #
            # if payload and self.action in [0, 1]:
            #     mail_subject = template.get_subject(**payload)
            #     mail_body = template.get_body(**payload)
            # else:
            #     mail_subject = ''
            #     mail_body = ''

            _body = template.body
            _subject = template.subject
            for obj in payload:
                available_obj = '{{ %s }}' % obj
                if available_obj in _subject:
                    _subject = _subject.replace(available_obj, str(payload[obj]))
                if available_obj in _body:
                    _body = _body.replace(available_obj, str(payload[obj]))
            inbox_subject = _subject
            inbox_body = _body

            if self.code == 'top_up' and self.action in [0, 2]:
                inbox_body = payload['body']

            if self.action in [0, 2]:
                inbox = Inbox.push(
                    sender=sender,
                    inbox_type=inbox_type,
                    inbox_content_id=inbox_content_id,
                    inbox_content_type=inbox_content_type,
                    title=inbox_subject,
                    body=inbox_body,
                    account=account,
                    trigger_id=self.id,
                )
                # for mobile app
                inbox.send_notification_fcm()
                inbox.status = 1
                inbox.datetime_send = timezone.now()
                inbox.save(update_fields=['status', 'datetime_send'])
                inbox.update_count_flag()

            '''
                close for manage less template (Not solid design)
            '''
            # if self.action in [0, 1]:
            #     if account.email is None:
            #         return
            #
            #     Mailer.push_and_send(
            #         mail_subject, mail_body, account
            #     )


class Template(models.Model):
    is_standard = models.BooleanField(default=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    event_trigger = models.ForeignKey(Trigger, null=True, blank=True, on_delete=models.CASCADE)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True)

    class Meta:
        default_permissions = DEFAULT_PERMISSIONS
        ordering = ['id']

    def get_subject(self, *args, **kwargs):
        _subject = self.subject

        for obj in kwargs:
            available_obj = '{{ %s }}' % obj
            if available_obj in self.subject:
                _subject = _subject.replace(available_obj, str(kwargs[obj]))
        # if 'parent_content_name' in kwargs and '{{ parent_content_name }}' in self.subject:
        #     _subject = _subject.replace('{{ parent_content_name }}', kwargs['parent_content_name'])
        return _subject

    def get_body(self, *args, **kwargs):
        from config.models import Config
        _body = self.body
        header_image = Config.pull_value('mailer-header-image')
        for obj in kwargs:
            available_obj = '{{ %s }}' % obj
            if available_obj in self.body:
                _body = _body.replace(available_obj, str(kwargs[obj]))
        # if 'email' in kwargs and '{{ email }}' in self.body:
        #     _body = _body.replace('{{ email }}', kwargs['email'])
        return render_to_string(
            'mails/base.html',
            {
                'header_image': settings.CO2_API_URL + header_image,
                'body': _body
            })
