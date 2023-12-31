import json
import time
from itertools import chain, groupby

from django.db import connection

from account.models import Account
from log.models import RequestLog
from utils.function_emoji import demojize


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if request.path_info.find('api') < 1 or request.path_info.find('api/account/delete/confirm/') >= 1:
            response = self.get_response(request)
            return response
        if request.__getattribute__('user'):
            account = request.user
        else:
            account = None
        if not account.id:
            account = None
        method = request.method
        try:
            payload = demojize(str(json.loads(request.body.decode('utf-8'))))
        except:
            payload = {}

        response = self.get_response(request)
        status_code = response.status_code
        RequestLog.objects.create(
            account=request.user if isinstance(request.user, Account) else None,
            method=method,
            path=path,
            payload=payload,
            status_code=status_code
        )
        return response

class QueryLogger:

    def __init__(self):
        self.queries = []

    def __call__(self, execute, sql, params, many, context):
        current_query = {'sql': sql, 'params': params, 'many': many}
        start = time.monotonic()
        try:
            result = execute(sql, params, many, context)
        except Exception as e:
            current_query['status'] = 'error'
            current_query['exception'] = e
            raise
        else:
            current_query['status'] = 'ok'
            return result
        finally:
            duration = time.monotonic() - start
            current_query['duration'] = duration
            self.queries.append(current_query)


class QueryCountDebugMiddleware(object):
    """
    This middleware will log the number of queries run and the total time taken for each request (with a
    status code of 200). It does not currently support multi-db setups.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_response(self, request, response):
        path = request.path
        if request.path_info.find('api') < 1 or request.path_info.find('api/account/delete/confirm/') >= 1:
            return response
        if response.status_code == 200:
            total_time = 0
            try:
                if len(connection.queries) == 1:
                    if connection.queries[0]['raw_sql'].startswith('SELECT "django_session"'):
                        return response
            except:
                pass
            sql_log = []
            unique_table = []
            for query in connection.queries:
                query_time = float(query.get('time'))
                if query_time is None:
                    query_time = query.get('duration', 0) / 1000
                sql_log.append(query['sql'])
                _sql = query['sql'].replace('`', '')
                _sql_list = _sql.split('FROM')
                _table_list = [x.split()[0] for x in _sql_list[1:]] if len(_sql_list) > 1 else []
                unique_table.append(_table_list)

                total_time += float(query_time)
            unique_table = list(chain.from_iterable(unique_table))
            total_table = len(set(unique_table))
            total_query = len(connection.queries)
            _score = ((total_query - 2) / total_table) if total_table > 0 else -1
            score = get_score(_score)
            result = {k: len(list(v)) for k, v in groupby(list(sorted(unique_table)), lambda x: x)}

            _path = '/'.join([parse_int(x) for x in path.split('/')])
            RequestLog.objects.create(
                account=request.user if isinstance(request.user, Account) else None,
                method='query-' + request.method,
                path=_path,
                payload=str(result),
                status_code='%s || %.2f/%s/%s => %d' % (
                    path, total_time, total_query, total_table, score
                )
            )
            # print('%.2f/%s/%s => %d' % (total_time, total_query, total_table, score))
            # print(unique_table)
            # print(sql_log)
            # print('\x1b[1;;43;30m==> %s queries run, total %s seconds    \x1b[0m' % (len(connection.queries), total_time))
        return response

def parse_int(x):
    if x.isnumeric():
        return 'ID'
    return x
def get_score(_score):
    score = 0
    if _score <= 1:
        score = 10
    elif _score > 4:
        score = 0
    elif _score > 3.5:
        score = 2
    elif _score > 2.5:
        score = 4
    elif _score >= 2:
        score = 5
    elif _score > 1.8:
        score = 6
    elif _score > 1.5:
        score = 7
    elif _score > 1.25:
        score = 8
    elif _score > 1:
        score = 9
    return score
