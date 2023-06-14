import time

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.core.cache import cache
from utils.caches.memcached_stats import MemcachedStats
from .views import check_permission
import re
import redis

@user_passes_test(check_permission)
def cache_view(request):
    key_list = []
    cache_settings = settings.CACHES.get('default', {})
    key = request.GET.get('key', '')
    if 'LOCATION' in cache_settings:
        backend = cache_settings.get('BACKEND')
        location = cache_settings.get('LOCATION', '')
        if backend == 'django_redis.cache.RedisCache':
            m = re.search("(.+?)://(.+?):(.+?)/(.+?)", location)
            _, host, port, db = m.groups('0')
            port, db = int(port), int(db)
            r = redis.Redis(host=host, port=port, db=db)
            for key in r.scan_iter('*%s*' % key):
                value = r.debug_object(key)
                size = value.get('serializedlength')
                key_list.append({
                    'key': key,
                    'size': size,
                    'time': r.ttl(key)
                })
                if len(key_list) > 1000:
                    break
        else:
            if ':' in location:
                host, port = settings.CACHES['default']['LOCATION'].split(':')
            else:
                host = settings.CACHES['default']['LOCATION']
                port = '11211'
            current_time = int(time.time())
            mem = MemcachedStats(host=host, port=port)
            for cached in mem.key_details(limit=0):
                d = {
                    'key': cached[0].split(':', 2)[2],
                    'size': cached[1],
                    'time': int(cached[2].split(' ')[0]) - current_time
                }
                key_list.append(d)

    return render(
        request,
        'console/cache.html',
        {
            'NAVBAR': 'cache',
            'key_list': key_list,
        }
    )


@user_passes_test(check_permission)
def cache_view_by_id(request, key):
    val = cache.get(key)
    return render(
        request,
        'console/cache_key.html',
        {
            'NAVBAR': 'cache-key',
            'key': key,
            'val': val,
        }
    )
