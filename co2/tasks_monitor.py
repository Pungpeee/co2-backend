from celery import shared_task
from django.utils import timezone
from django.core.cache import cache

from utils.base_task import BaseAlertTask
from utils.caches.time_out import get_time_out
from time import sleep
from celery import shared_task


def _set_cached(key):
    cache.set('monitor_node_' + key, timezone.now(), get_time_out())

@shared_task(bind=True, queue='user')
def task_print_value(self, value):
    print(value)
    return 'Successfully!'


@shared_task(bind=True, queue='user')
def task_print_value_and_sleep(self, value, time):
    print(value)
    sleep(time)
    return 'Successfully!'


@shared_task(bind=True, queue='user')
def task_fail(self):
    print(1 / 0)
    return 'Failed!'


@shared_task(bind=True, queue='user')
def task_memory(self, memory_byte, time):
    var = ' ' * memory_byte * 2  # 512000000 ~ 0.5 GB
    sleep(time)
    return 'Successfully!'

@shared_task(bind=True, base=BaseAlertTask, queue='user')
def task_set_timer_user(self):
    _set_cached('user')
    return 'Done.'


@shared_task(bind=True, base=BaseAlertTask, queue='dashboard')
def task_set_timer_dashboard(self):
    _set_cached('dashboard')
    return 'Done.'


@shared_task(bind=True, base=BaseAlertTask, queue='export')
def task_set_timer_export(self):
    _set_cached('export')
    return 'Done.'


@shared_task(bind=True, base=BaseAlertTask, queue='encode')
def task_set_timer_encode(self):
    _set_cached('encode')
    return 'Done.'


# For priority test
@shared_task(bind=True, base=BaseAlertTask, queue='user')
def task_sleep_low(self):
    return 'LOW'


# For priority test
@shared_task(bind=True, base=BaseAlertTask, queue='user')
def task_sleep_high(self):
    return 'HIGH'


# For priority test
@shared_task(bind=True, base=BaseAlertTask, queue='user')
def task_sleep_default(self):
    return 'DEFAULT'
