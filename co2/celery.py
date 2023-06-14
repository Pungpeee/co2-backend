from __future__ import absolute_import, unicode_literals
import logging
import os

from celery import Celery, signals
from kombu.common import Broadcast
from django.conf import settings

from co2.settings import INSTALLED_APPS, TIME_ZONE, ENABLE_LOGGING, RESULT_BACKEND, CELERY_BROKER_URL

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)
# set the default Django settings module for the 'celery' program.
logger_celery = logging.getLogger('co2_celery')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'co2.settings')

app = Celery('co2', backend=RESULT_BACKEND, broker=CELERY_BROKER_URL)


def my_on_success(self, exc, task_id, args, kwargs):
    log_data = {
        "task_id": task_id,
        "task_name": self.name,
        "return_message": exc,
        "args": args,
        "kwargs": kwargs,
    }
    logger_celery.info(msg=log_data)

def my_on_failure(self, exc, task_id, args, kwargs, einfo):
    from alert.models import Alert
    log_data = {
        "task_id": task_id,
        "task_name": self.name,
        "return_message": exc,
        "args": args,
        "kwargs": kwargs,
        "error_info": str(einfo)
    }
    logger_celery.info(msg=log_data)
    alert = Alert.pull_by_id(task_id)
    if alert:
        alert.set_failed(einfo)

app.conf.update(
    timezone=TIME_ZONE,
    result_expires=30,
    result_backend=RESULT_BACKEND,
    CELERY_TASK_TRACK_STARTED = True,
    # task_default_priority=5,
    # task_queue_max_priority=10,
    task_annotations = {'*': {'on_success': my_on_success, 'on_failure': my_on_failure}}
)


app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# Logging
if ENABLE_LOGGING:
    @signals.setup_logging.connect
    def on_celery_setup_logging(loglevel, logfile, format, colorize, **kwargs):
        pass

for app_name in INSTALLED_APPS:
    if app_name.startswith('django'):
        continue
    try:
        p = os.listdir(app_name)
    except:
        continue
    for _ in p:
        if _.find('tasks') == -1:
            continue
        if _.find('.pyc') != -1:
            continue
        if not _.endswith('.py') or _.startswith('.'):
            continue
        app.autodiscover_tasks([app_name], related_name=_)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))