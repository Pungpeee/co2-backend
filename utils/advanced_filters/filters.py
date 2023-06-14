from django.contrib.contenttypes.models import ContentType
from emoji import demojize
from rest_framework.filters import SearchFilter, OrderingFilter, BaseFilterBackend


def _getattr(o, name, default):
    name = '.'.join(name.split('__'))
    for attr in name.split('.'):
        o = getattr(o, attr, default)
    if type(o) == ContentType:
        o = '.'.join(o.natural_key())
    return o


class SearchFilter(SearchFilter):  # not avaliable for ManyToManyField
    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = ' '.join(self.get_search_terms(request)).lower()
        if not search_fields or not search_terms:
            return queryset
        remove_list = []
        for o in queryset:
            found = False
            for o_data in [_getattr(o, x, None) for x in search_fields]:
                if o_data is not None and str(o_data).lower().find(search_terms) != -1:
                    found = True
                    break
            if not found:
                remove_list.append(o)
        if type(queryset) == list:
            [queryset.remove(o) for o in remove_list]
        else:
            queryset = queryset.exclude(id__in=[o.id for o in remove_list])
        return queryset

    def get_search_terms(self, request):
        params = request.query_params.get(self.search_param, '')
        params = params.replace('\x00', '')  # strip null characters
        params = params.replace(',', ' ')
        params = demojize(params)
        return [params]  # params.split()


def resolution_ordering_list(_list, ordering):
    if ordering == []:
        return _list
    key = ordering[0]
    reverse = False
    if key.startswith('-'):
        key = key[len('-'):]
        reverse = True
    values_set = set(map(lambda o: _getattr(o, key, None), _list))
    values_set = sorted(values_set, reverse=reverse, key=lambda o: (o is None, str(o).lower() if type(o) is str else o))
    group_list = [[o for o in _list if _getattr(o, key, None) == values] for values in values_set]
    result = []
    for _list in group_list:
        if len(_list) == 1:
            result += _list
        else:
            result += resolution_ordering_list(_list, ordering[1:])
    return result


class OrderingFilter(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if ordering:
            if type(queryset) is list:
                return resolution_ordering_list(queryset, ordering)
            else:
                _list = resolution_ordering_list(list(queryset), ordering)
                _id_list = [o.id for o in _list]
                ordering = 'FIELD(`id`, %s)' % ','.join(str(id) for id in _id_list)
                return queryset.filter(id__in=_id_list).extra(select={'ordering': ordering}, order_by=('ordering',))
        return queryset


def multiple_compare(value, lookup_value):
    for lookup in lookup_value.split(','):
        if lookup == 'true':
            lookup = 'True'
        elif lookup == 'false':
            lookup = 'False'
        if str(value) == lookup:
            return True
    return False


class FilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filterset_fields = getattr(view, 'filter_fields', None)
        lookup = {params: request.query_params[params] for params in request.query_params if params in filterset_fields}
        if lookup is {}:
            return queryset
        remove_list = []
        for o in queryset:
            for filter in lookup:
                if not multiple_compare(_getattr(o, filter, None), lookup[filter]):
                    remove_list.append(o)
                    break
        remove_list = list(dict.fromkeys(remove_list))
        if type(queryset) == list:
            [queryset.remove(o) for o in remove_list]
        else:
            queryset = queryset.exclude(id__in=[o.id for o in remove_list])
        return queryset
