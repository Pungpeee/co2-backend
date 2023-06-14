from django.conf import settings
from django.db import models
from django.utils import timezone
from rest_framework import status

from account.models import Account
from config.models import Config
from log.models import Log
from notification_template.models import Trigger


class Inbox(models.Model):
    TYPE_CHOICES = (
        # Single message
        (1, 'Direct Message'),
        (2, 'News Update')
    )

    STATUS_CHOICES = (
        (-2, 'FCM Failed'),
        (-1, 'Failed'),
        (0, 'Draft'),
        (1, 'Sent'),
    )

    account = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)

    type = models.IntegerField(choices=TYPE_CHOICES, default=1)
    trigger = models.ForeignKey('notification_template.Trigger', null=True, on_delete=models.SET_NULL)

    title = models.TextField(blank=True)
    body = models.TextField(blank=True)
    detail = models.TextField(blank=True)
    image = models.ImageField(upload_to='inbox/%Y/%m/', null=True, blank=True)

    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, blank=None, null=True)
    content_id = models.PositiveIntegerField(blank=True, null=True)

    count_read = models.IntegerField(default=0)
    count_send = models.IntegerField(default=1)

    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    datetime_send = models.DateTimeField(null=True)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-datetime_create']
        default_permissions = ()

    def __str__(self):
        return "%s" % (self.id)

    @property
    def config_fcm(self):
        return Config.pull_value('notification-client-list')

    @property
    def config_mail(self):
        return Config.pull_value('notification-email-list')

    @property
    def is_read(self):
        return self.read_set.filter(inbox=self).exists()

    @property
    def click_action(self):
        from django.conf import settings
        if self.type == 1:
            return 'OPEN_DIRECT_MESSAGE_DETAIL'
        elif self.type == 2:
            return 'OPEN_NEWS_UPDATE_DETAIL'
        else:
            word = self.content_type.app_label.upper()
            return 'OPEN_%s_DETAIL' % word

    @staticmethod
    def push(sender,
             inbox_type,
             inbox_content_type=None,
             inbox_content_id=None,
             title='',
             body='',
             detail='',
             account=None,
             account_list=None,
             trigger_id=None):
        # Get Account list from chager device account

        from django.db.models.query import QuerySet
        from account.models import Account
        from .caches import cache_account_count
        if isinstance(sender, int):
            sender = Account.objects.filter(id=sender).first()
        elif isinstance(sender, dict):
            sender_list = sender.values()
            account_id = sender_list.pop(0)
            account = Account.objects.filter(id=account_id)
            if account.exists():
                account = account.first()
            else:
                account = None

        else:
            sender = None

        inbox = Inbox.objects.create(
            account=sender,
            type=inbox_type,
            title=title,
            body=body,
            detail=detail,
            status=0,
            content_type=inbox_content_type,
            content_id=inbox_content_id,
            trigger_id=trigger_id
        )

        # Clear notification
        if sender or account:
            count = cache_account_count(sender if sender else account)
            count.add()

        if account is not None:
            if isinstance(account, QuerySet):
                inbox.member_set.create(account=account)
            elif isinstance(account, int):
                inbox.member_set.create(account_id=account)
            elif isinstance(account, dict):
                inbox.member_set.create(**account)
            elif isinstance(account, Account):
                inbox.member_set.create(account=account)

        if account_list is not None:
            if isinstance(account_list, QuerySet):
                for account in account_list:
                    if isinstance(account, dict):
                        account_id = account.get('account_id', None)
                        if account_id is None:
                            account_id = account.get('id', None)
                        if account_id is not None:
                            inbox.member_set.get_or_create(account_id=account_id)
                    elif hasattr(account, 'account_id'):
                        inbox.member_set.get_or_create(account_id=getattr(account, 'account_id'))
                    elif isinstance(account, Account):
                        inbox.member_set.get_or_create(account=account)
                    elif isinstance(account, int):
                        inbox.member_set.get_or_create(account_id=account)
            elif isinstance(account_list, list):
                for account_id in account_list:
                    if isinstance(account_id, int):
                        inbox.member_set.get_or_create(account_id=account_id)
                    elif isinstance(account_id, dict):
                        data_template = {'account_id': -1}
                        if account_id.keys() == data_template.keys():
                            inbox.member_set.get_or_create(**account_id)
                    elif isinstance(account_id, Account):
                        inbox.member_set.get_or_create(account_id=account_id.id)
        return inbox

    @staticmethod
    def push_news_update(news_update, is_queue):
        from .tasks_push_news_update import task_push_news_update
        if is_queue:
            task_push_news_update.delay(news_update.id)
        else:
            task_push_news_update(**{'news_update_id': news_update.id})

    @staticmethod
    def push_news_update_force_send(news_update, is_queue):
        from .tasks_push_news_update import task_push_news_update_force_send
        if is_queue:
            task_push_news_update_force_send.delay(news_update.id)
        else:
            task_push_news_update_force_send(**{'news_update_id': news_update.id})

    def get_body_fcm_data(self):
        from inbox.serializer_fcm import FCMInboxSerializer
        if self.type in [1, 2]:
            return FCMInboxSerializer(instance=self).data

    def send_notification(self):
        if not settings.TESTING:
            # For sms and mail
            device_list = Config.pull_value('notification-device-list')
            if settings.IS_SEND_FCM and 'fcm' in device_list:
                self.send_notification_fcm()
            self.status = 1
            self.datetime_send = timezone.now()
            self.save(update_fields=['status', 'datetime_send'])
            self.update_count_flag()

    def update_count_flag(self):
        from .caches import cache_account_count_delete
        account_id_list = self.member_set.all().values_list('account_id', flat=True)
        Count.objects.filter(account_id__in=account_id_list).update(count=1)
        for account_id in account_id_list:
            cache_account_count_delete(account_id)

    def send_notification_fcm(self):
        setting = self.config_fcm['settings']
        api_key_list = setting['FCM_SERVER_KEY']

        api_key = api_key_list[0]

        for account_id in self.member_set.values_list('account_id', flat=True):
            data = self.get_body_fcm_data()
            try:
                self._send_fcm(account_id=account_id,
                               title=self.title,
                               body=self.body,
                               click_action=self.click_action,
                               data=data,
                               server_key=api_key)
            except Exception as error:
                Log.push(None, 'ACCOUNT',
                         'SENT NOTIFICATION', None, 'Have something wrong with FCM',
                         status.HTTP_400_BAD_REQUEST, payload=dict(error))

                print('Fcm error %s' % error)

    def _send_fcm(self, account_id, title, body, data, click_action, server_key, **kwargs):
        from fcm_django.models import FCMDevice
        from fcm_django.fcm import fcm_send_message
        account_register_list = FCMDevice.objects.filter(user_id=account_id, active=True)
        if account_register_list.exists():
            for account_register in account_register_list:
                if account_register.type == u'android':
                    badge = Inbox.objects.filter(read__isnull=True, member__account_id=account_id).count()
                    sound = 'default'
                elif account_register.type == u'ios':
                    sound = 'default'
                    badge = Inbox.objects.filter(status=1, member__account_id=account_id, read__isnull=True).count()
                else:
                    continue

                result = fcm_send_message(registration_id=account_register.registration_id,
                                          title=title,
                                          body=body,
                                          data=data,
                                          badge=badge,
                                          sound=sound,
                                          click_action=click_action,
                                          api_key=server_key,
                                          **kwargs)
                if result['success'] == 0:
                    account_register.active = False
                    account_register.save(update_fields=['active'])


    # def send_notification_email(self):
    #     from mailer.models import Mailer
    #     from account.models import Account
    #     from utils.content import get_content
    #     from .mail import get_body, get_subject
    #     if not Config.pull_value('config-mailer-is-enable') or settings.IS_LOCALHOST:
    #         return
    #
    #     for account_id in self.member_set.values_list('account_id', flat=True):
    #         account = Account.pull(account_id)
    #
    #         if account.email is None and not account.is_subscribe:
    #             return
    #
    #         email = account.email
    #         body = get_body(self, account)
    #         subject = get_subject(self)
    #         attach_file = None
    #         mailer = Mailer.objects.create(
    #             subject=subject,
    #             body=body,
    #             to=email,
    #             type=2,
    #             attach_file=attach_file,
    #             inbox=self
    #         )
    #
    #         # Transaction For Event Success
    #         if self.type == 11:
    #             transaction = Transaction.pull(self.content_id)
    #             content = get_content(transaction.content_type_id, transaction.content_id)
    #             if content is not None:
    #                 if transaction.content_type_id == settings.CONTENT_TYPE('event.event').id:
    #                     if content.is_session_enrollment_config_enabled:
    #                         session_enroll_id_list = SessionEnrollment.pull_list(transaction).values_list('session_id',
    #                                                                                                       flat=True).exclude(
    #                             session__type=0)
    #                         session_list = Session.objects.filter(id__in=session_enroll_id_list)
    #                         if session_enroll_id_list.exists():
    #                             session_first = session_list.first()
    #                             session_last = session_list.last()
    #                             calendar = create_ics_file('Event Calendar', content.name, session_first.datetime_start,
    #                                                        session_last.datetime_end)
    #                             mailer.attach_file.save('invite.ics', ContentFile(calendar.to_ical()))
    #                     else:
    #                         calendar = create_ics_file('Event Calendar', content.name, content.datetime_start,
    #                                                    content.datetime_end)
    #                         mailer.attach_file.save('invite.ics', ContentFile(calendar.to_ical()))
    #
    #         if body is None:
    #             return
    #
    #         mailer.send()


class Member(models.Model):
    inbox = models.ForeignKey(Inbox, on_delete=models.CASCADE)
    account = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+', on_delete=models.CASCADE)
    sort = models.IntegerField(default=0, db_index=True)

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        default_permissions = ()
        ordering = ['id']

    def __str__(self):
        return '%s' % self.account.email


class Count(models.Model):
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

    is_updated = models.BooleanField(default=False, db_index=True)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True)

    class Meta:
        default_permissions = ()

    @staticmethod
    def pull(account):
        from .caches import cache_account_count
        return cache_account_count(account)

    def add(self):
        from .caches import cache_account_count_delete
        self.count += 1
        self.save(update_fields=['count'])
        cache_account_count_delete(self.account.id)

    def clear_count(self):
        from .caches import cache_account_count_delete
        self.count = 0
        self.save(update_fields=['count'])
        cache_account_count_delete(self.account.id)


class Read(models.Model):
    inbox = models.ForeignKey(Inbox, on_delete=models.CASCADE)
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    datetime_create = models.DateTimeField(auto_now_add=True)
    datetime_update = models.DateTimeField(auto_now=True)

    class Meta:
        default_permissions = ()

    @staticmethod
    def is_read(inbox, account):
        return Read.objects.filter(
            inbox=inbox,
            account=account
        ).exists()
