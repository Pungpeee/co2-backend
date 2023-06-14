from django.core.cache import cache

from utils.caches.time_out import get_time_out
from .models import ContentView


def cache_content_view(content_type, content_id):
    key = 'analytic_content_view__%s_%s' % (content_type.id, content_id)
    result = cache.get(key)
    if result is None:
        result = ContentView.objects.filter(content_id=content_id, content_type_id=content_type.id).first()
        if result is None:
            result = ContentView.objects.create(
                content_id=content_id,
                content_type_id=content_type.id,
                count=0
            )
        cache.set(key, result, get_time_out())
    return result


def cache_content_view_set(content_type_id, content_id, content_view):
    key = 'analytic_content_view__%s_%s' % (content_type_id, content_id)
    cache.set(key, content_view, get_time_out())


def cache_content_view_count(content_type, content_id):
    key = 'analytic_content_view_count_%s_%s' % (content_type.id, content_id)
    result = cache.get(key)
    if result is None:
        content_view = ContentView.objects.filter(content_id=content_id, content_type=content_type).first()
        if content_view is None:
            content_view = ContentView.objects.create(
                content_id=content_id,
                content_type=content_type
            )
        result = content_view.count
        cache.set(key, result, get_time_out())
    return result


def cache_content_view_count_set(content_type_id, content_id, value):
    key = 'analytic_content_view_count_%s_%s' % (content_type_id, content_id)
    cache.set(key, value, get_time_out())
