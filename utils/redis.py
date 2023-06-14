import redis

from django.conf import settings

# Note: https://redis.io/commands
from django.core.cache import cache


def set_value(key, value):
    return settings.REDIS.set(key, value)


def push(key, value):
    return settings.REDIS.lpush(key, value)


def pop(key):
    return settings.REDIS.lpop(key)


def length(key):
    return settings.REDIS.llen(key)


def is_exists(key):
    return bool(settings.REDIS.exists(key))


def find_key(pattern):
    return list(map(lambda k: k.decode('utf-8'), settings.REDIS.keys(pattern)))


def get(key):
    type = settings.REDIS.type(key).decode('utf-8')
    if type == 'string':
        return settings.REDIS.get(key)
    elif type == 'list':
        return settings.REDIS.lrange(key, 0, -1)
    return None


def mget(key_list):
    return list(filter(None, settings.REDIS.mget(key_list)))


def get_value(key):
    return get(key)


def delete_value(key):
    settings.REDIS.delete(key)


def cache_connect():
    location = settings.CACHES['default']['LOCATION']
    host, port_db = location.split('//')[1].split(':')
    port, db = port_db.split('/')
    return redis.StrictRedis(host=host, port=port, db=db)


def cache_delete_with_prefix(prefix):
    r = cache_connect()
    key_list = []
    for key in r.scan_iter(':1:' + prefix + '*'):
        _key = key.decode("utf-8").replace(':1:', '')
        key_list.append(_key)
    cache.delete_many(key_list)
