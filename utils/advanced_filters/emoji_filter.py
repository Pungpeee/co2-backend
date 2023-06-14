from rest_framework.filters import SearchFilter
from utils.function_emoji import demojize


class SearchFilter(SearchFilter):
    def get_search_terms(self, request):
        params = request.query_params.get(self.search_param, '')
        params = params.replace('\x00', '')  # strip null characters
        params = params.replace(',', ' ')
        params = demojize(params)
        return [params]  # params.split()


class SearchFilterAccount(SearchFilter):
    def get_search_terms(self, request):
        params = request.query_params.get(self.search_param, '')
        params = params.replace('\x00', '')  # strip null characters
        params = params.replace(',', ' ')
        params = demojize(params)
        return params.split()
