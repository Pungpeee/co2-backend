import json

from functools import reduce

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from operator import or_
from django.conf import settings


# from utils.model_permission import
class Log(models.Model):
    external_id = models.CharField(max_length=32, blank=True, null=True, default=None, db_index=True)
    group = models.CharField(max_length=60, db_index=True)
    code = models.CharField(max_length=60, db_index=True)

    account_id = models.BigIntegerField(default=-1)
    account_code = models.CharField(max_length=32, db_index=True, blank=True, null=True, default=None)
    account_name = models.CharField(max_length=255, blank=True, null=True)
    account_username = models.CharField(max_length=150, blank=True, null=True)
    account_email = models.CharField(max_length=255, blank=True, null=True)
    account_image = models.ImageField(blank=True, null=True)

    content_type = models.ForeignKey(ContentType, related_name='+', on_delete=models.CASCADE, null=True)
    content_id = models.IntegerField(default=-1)
    content = GenericForeignKey('content_type', 'content_id')

    ip = models.GenericIPAddressField(null=True, blank=True)
    note = models.TextField(blank=True)
    payload = models.TextField(blank=True, default='{}')  # JSON
    data_old = models.TextField(blank=True, default='{}')  # JSON
    data_new = models.TextField(blank=True, default='{}')  # JSON

    status = models.CharField(max_length=120, blank=True)
    status_code = models.PositiveIntegerField(db_index=True)

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'log.log'
        ordering = ['-datetime_create']

    def __str__(self):
        return str(self.id)

    @staticmethod
    def push(request, group, code, account, status, status_code,
             content_type=None, content_id=-1, payload={},
             note='', data_old='{}', data_new='{}', data_change='{}', external_id=None):

        from utils.ip import get_client_ip
        from config.models import Config
        # is_log_enable = Config.pull_value('config-log-db-enabled')
        # if not is_log_enable:
        #     return True

        if request and request.user.is_authenticated:
            ip = get_client_ip(request)
            account_id = request.user.id
            account_username = request.user.username
            account_code = request.user.code
            account_name = request.user.get_full_name()
            account_email = request.user.email
            account_image = request.user.image
        elif account:
            ip = get_client_ip(request)
            account_id = account.id
            account_username = account.username
            account_code = account.code
            account_name = account.get_full_name()
            account_email = account.email
            account_image = account.image
        else:
            ip = get_client_ip(request)
            account_id = -1
            account_name = None
            account_username = None
            account_code = None
            account_email = None
            account_image = None

        if data_change != '{}':
            old_data = {}
            new_data = {}
            for key in data_change:
                if key in data_old and key in data_new:
                    old_data[key] = str(data_old[key])
                    new_data[key] = str(data_new[key])
            data_old = old_data
            data_new = new_data

        log = Log.objects.create(
            code=code,
            group=group,
            account_id=account_id,
            account_username=account_username,
            account_code=account_code,
            account_name=account_name,
            account_email=account_email,
            account_image=account_image,
            content_type=content_type,
            content_id=content_id,
            ip=ip,
            note=note,
            payload=payload,
            data_old=json.dumps(data_old),
            data_new=json.dumps(data_new),
            status=status,
            status_code=status_code,
            external_id=external_id
        )
        # graylog_push_info_udp('log', model_to_dict(log))
        return log

    @staticmethod
    def push_content_log(
            group, code,
            content_type=None, content_id=-1,
            note='',
            data_old='{}', data_new='{}', data_change='{}'
    ):
        if data_change != '{}':
            old_data = {}
            new_data = {}
            for key in data_change:
                if key in data_old and key in data_new:
                    old_data[key] = data_old[key]
                    new_data[key] = data_new[key]
            data_old = old_data
            data_new = new_data
        return Log.objects.create(
            code=code,
            group=group,
            content_type=content_type,
            content_id=content_id,
            note=note,
            data_old=json.dumps(data_old),
            data_new=json.dumps(data_new),
            status='success',
            status_code=200,
        )

    @staticmethod
    def pull_code(code):
        return Log.objects.filter(code=code)

    @staticmethod
    def pull_by_multiple_code(code_list):
        query = reduce(or_, [Q(code=code) for code in code_list])
        return Log.objects.filter(query)  # .values_list('pk', flat=True)

class RequestLog(models.Model):
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    method = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    payload = models.TextField(blank=True, default='{}')
    status_code = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
