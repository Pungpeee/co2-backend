from django.core.cache import cache
from django.db.models import Case, When

from analytic.models import ContentView
from learning_content.models import LearningContent
from utils.advanced_filters.filters import resolution_ordering_list
from utils.caches.time_out import get_time_out, get_time_out_short
from django.contrib.contenttypes.models import ContentType


def cache_learning_content_view(content_type_list):
    key = 'content_learning_view'
    result = cache.get(key)
    if result is None:
        try:
            content_view = ContentView.objects.filter(content_type__in=content_type_list).order_by('-monthly_count')
            dict_content_view = {(o.content_type.id, o.content_id): o.monthly_count for o in content_view}
            result = {k: v for k, v in sorted(dict_content_view.items(),
                                              key=lambda item: item[1],
                                              reverse=True)}
            cache.set(key, result, get_time_out_short())
        except:
            result = None

    return result

def cache_content_view(content_type):
    key = 'content_view_%s' % content_type.id
    result = cache.get(key)
    if result is None:
        try:
            content_list = list(content_type.model_class().objects.all())
            content_view = ContentView.objects.filter(content_type=content_type)
            _dict_content_view = {o.content_id: o.monthly_count for o in content_view}
            ordering = ['-monthly_count']
            [setattr(o, 'monthly_count', _dict_content_view.get(o.id, 0)) for o in content_list]
            ordered_list = resolution_ordering_list(content_list, ordering)
            ordered_id_list = [o.id for o in ordered_list]
            result = ordered_id_list
            cache.set(key, result, get_time_out())
        except:
            result = None
    return result


def popular_filter(queryset):
    content_type = ContentType.objects.get_for_model(queryset.model)
    _id_list = cache_content_view(content_type)
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(_id_list)])
    return queryset.all().order_by(preserved)

def popular_learning_content_queryset_filter(queryset):
    content_type_list = LearningContent.get_all_content_type_list()
    dict_content = cache_learning_content_view(content_type_list)
    count_dict_content = len(dict_content)
    preserved = Case(*[When(content_type_id=k[0], content_id=k[1], then=pos) for pos, k in enumerate(dict_content)],
                     default=count_dict_content)
    return queryset.order_by(preserved)
