from django.core.cache import cache

from utils.caches.time_out import get_time_out, get_time_out_day
from .models import Config
from .serializers import ConfigSerializer

KEY_CONFIG_TAG_TYPE = 'config_config_tag_type'


def cache_config(code):
    key = 'config_%s' % code
    result = cache.get(key)
    if result is None:
        result = Config.objects.filter(code=code).first()
        if result is None:
            result = Config.init_code(code)
            if result:
                # TODO : push to log center (bug call config fail)
                pass
        if result:
            cache.set(key, result, get_time_out())
    return result


def cache_config_delete(code):
    key = 'config_%s' % code
    cache.delete(key)

def cache_config_tag_type_delete(code):
    if code.startswith('tag-'):
        cache.delete(KEY_CONFIG_TAG_TYPE)

def cache_config_result_web_delete():
    key = 'config_result_web'
    cache.delete(key)


def cache_config_result_dashboard():
    key = 'config_result_dashboard'
    result = cache.get(key)
    if result is None:
        try:
            result = {}
            for config in Config.objects.filter(is_dashboard=True):
                result[config.code] = ConfigSerializer(config).data
            cache.set(key, result, get_time_out_day())
        except:
            result = -1
    return None if result == -1 else result


def cache_config_result_dashboard_delete():
    key = 'config_result_dashboard'
    cache.delete(key)


def cache_config_last_update_web():
    key = 'config_last_update_web'
    result = cache.get(key)
    if result is None:
        config = Config.objects.filter(is_web=True).order_by('-datetime_update').first()
        if config:
            result = config.datetime_update
        else:
            result = -1
        cache.set(key, result, get_time_out_day())
    return None if result == -1 else result


def cache_config_last_update_web_delete():
    key = 'config_last_update_web'
    cache.delete(key)


def cache_config_last_update_dashboard():
    key = 'config_last_update_dashboard'
    result = cache.get(key)
    if result is None:
        config = Config.objects.filter(is_dashboard=True).order_by('-datetime_update').first()
        if config:
            result = config.datetime_update
        else:
            result = -1
        cache.set(key, result, get_time_out_day())
    return None if result == -1 else result


def cache_config_last_update_dashboard_delete():
    key = 'config_last_update_dashboard'
    cache.delete(key)


# def config_cached_refresh():
#     from filter.caches import cache_filter_update_web_delete
#     from filter.caches import cache_filter_update_dashboard_delete
#     Config.set_value('config-update', True)
#     cache_config_last_update_web_delete()
#     cache_config_result_web_delete()
#     cache_filter_update_web_delete()
#     cache_filter_update_dashboard_delete()


def cache_config_tag_type():
    key = KEY_CONFIG_TAG_TYPE
    result = cache.get(key)
    if result is None:
        config_tag_list = list(Config.objects.filter(app='tag', code__startswith='tag-').values_list('code',
                                                                                                     flat=True))
        if len(config_tag_list) > 0:
            result = [config_tag.split('tag-')[1].split('-is-display')[0].replace('-', '_').upper() for config_tag in config_tag_list]
            cache.set(key, result, get_time_out_day())
        else:
            result = []

    return result