from __future__ import absolute_import, unicode_literals

from celery import shared_task

from alert.models import Alert


def test():
    return test_task.delay('jade')

@shared_task
def add(x, y, alert_id):
    try:
        alert = Alert.objects.get(id=alert_id, code='log.test_tasks.2')
    except:
        return 'Alert Not Found.'
    alert.status = 3
    alert.save(update_fields=['status'])
    return x + y

@shared_task
def test_task(name, alert_id):
    print('TEST DONE, HI %s, 1' % name)
    print('TEST DONE, HI %s, 2' % name)
    print('TEST DONE, HI %s, 3' % name)
    print('TEST DONE, HI %s, 4' % name)
    try:
        alert = Alert.objects.get(id=alert_id, code='log.test_tasks.1')
    except:
        return 'Alert Not Found.'
    alert.status = 3
    alert.save(update_fields=['status'])
    return 'TEST DONE, HI %s, 5' % name


@shared_task(name='celery.ping')
def ping():
    return 'pong'

