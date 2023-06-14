from celery import Task

from alert.models import Alert
from django.conf import settings as _settings
from itertools import chain, groupby


class BaseAlertTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        alert = Alert.pull_by_id(task_id)
        if alert:
            alert.set_failed(einfo)
