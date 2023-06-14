from django.core.cache import cache

from config.models import Config
from utils.caches.time_out import get_time_out
from .models import NewsUpdate, NewsUpdateLog


def cache_news_update_pull_list():
    key = 'news_update_pull_list'
    result = cache.get(key)
    if result is None:
        try:
            result = NewsUpdate.objects.filter(is_display=True).order_by('-is_pin', '-datetime_update')
            cache.set(key, result, get_time_out())
        except NewsUpdate.DoesNotExist:
            result = -1
    return None if result == -1 else result


def cache_news_update_pull_list_delete():
    key = 'news_update_pull_list'
    cache.delete(key)
    key = 'news_update_home_pull_list'
    cache.delete(key)


def cache_news_home_web_news_update_delete():
    key = 'home_web_news_update'
    cache.delete(key)
    cache.delete('home_news_update_')


def cached_news_update(news_updated_id):
    key = 'news_updated_%s' % news_updated_id
    result = cache.get(key)
    if result is None:
        try:
            result = NewsUpdate.objects.filter(id=news_updated_id).first()
            cache.set(key, result, get_time_out())
        except NewsUpdate.DoesNotExist:
            result = -1
    return None if result == -1 else result


def cache_news_update_delete(news_updated_id):
    key = 'news_updated_%s' % news_updated_id
    cache.delete(key)


def cached_news_update_cover(news_updated_id):
    key = 'news_updated_cover_%s' % news_updated_id
    result = cache.get(key)
    if result is None:
        try:
            news = NewsUpdate.pull(news_updated_id)
            result = news.gallery_set.filter(is_cover=True).first()
            cache.set(key, result, get_time_out())
        except NewsUpdate.DoesNotExist:
            result = -1
    return None if result == -1 else result


def cached_news_announcement():
    key = 'news_announcement'
    result = cache.get(key)
    if result is None:
        try:
            result = NewsUpdate.objects.filter(is_pin=True).select_related('account')
            cache.set(key, result, get_time_out())
        except NewsUpdate.DoesNotExist:
            result = -1
    return None if result == -1 else result


def cached_news_announcement_delete():
    key = 'news_announcement'
    cache.delete(key)


def cache_news_update_cover_delete(news_updated_id):
    key = 'news_updated_cover_%s' % news_updated_id
    cache.delete(key)


def cache_news_update_home_pull_list():
    key = 'news_update_home_pull_list'
    result = None
    if result is None:
        try:
            result = NewsUpdate.objects.filter(is_display=True).order_by('-datetime_update')
            cache.set(key, result, get_time_out())
        except NewsUpdate.DoesNotExist:
            result = -1
    return None if result == -1 else result


def cache_news_update_log(news_update_id, account_id):
    key = 'news_update_%s_account_%s' % (news_update_id, account_id)
    result = cache.get(key)
    if result is None:
        result = NewsUpdateLog.objects.filter(news_update_id=news_update_id, account_id=account_id).first()
        cache.set(key, result if result else -1, get_time_out())
    return None if result == -1 else result


def cache_news_update_all_log_delete(news_update_id):
    log_list = NewsUpdateLog.objects.values_list('account_id', flat=True).order_by('account_id').distinct()
    keys = ['news_update_%s_account_%s' % (news_update_id, account_id) for account_id in log_list]
    cache.delete_many(keys)


def cache_news_update_log_delete(news_update_id, account_id):
    key = 'news_update_%s_account_%s' % (news_update_id, account_id)
    cache.delete(key)


# home_news_update_api
def clear_caches(objects):
    key_list = [
        'news_update_pull_list',
        'home_web_news_update',
        'news_announcement',
        'home_news_update_api_%s' % Config.pull_value('home-limit-item'),
        'news_updated_%s' % objects.id,
        'news_updated_cover_%s' % objects.id,
        'news_update_%s_account_' % objects.id,
    ]
    for key in key_list:
        cache.delete(key)
