from django.core.cache import cache

from utils.caches.time_out import get_time_out
from .models import Term


def cache_term(id):
    key = 'term_%s' % id
    result = cache.get(key)
    if result is None:
        result = Term.objects.filter(id=id).first()
        cache.set(key, result, get_time_out())
    return result
