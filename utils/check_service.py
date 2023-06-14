# from django.conf import settings
from django.db import connections, OperationalError
from django.core.cache import cache
from celery import Celery
from kombu import Connection
from pymongo import MongoClient


def check_redis():
    from co2.settings import REDIS
    try:
        REDIS.ping()
    except:
        connected = False
    else:
        connected = True
    return connected


def check_mariadb():
    db_conn = connections['default']
    try:
        db_conn.cursor()
    except OperationalError:
        connected = False
    else:
        connected = True
    return connected


def check_memcached():
    cache.set('check_connection', True, 10)
    return cache.get('check_connection', False)


def check_rabbitmq():
    try:
        from co2.local_setting import CELERY_BROKER_URL
    except:
        from co2.settings import CELERY_BROKER_URL
    try:
        conn = Connection(CELERY_BROKER_URL)
        conn.ensure_connection(max_retries=1)
    except:
        connected = False
    else:
        connected = True
    return connected


# def check_mongodb():
#     from django.conf import settings
#     client = MongoClient(host=settings.MONGODB_HOST, port=int(settings.MONGODB_PORT), serverSelectionTimeoutMS=2000)
#     try:
#         client.server_info()
#     except:
#         return False
#     return True


def check_service():
    return {
        'status_mariadb': check_mariadb(),
        # 'status_mongodb': check_mongodb(),
        'status_redis': check_redis(),
        'status_memcached': check_memcached(),
        'status_rabbitmq': check_rabbitmq()
    }
