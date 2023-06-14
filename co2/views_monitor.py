import time

from django.core.cache import cache
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .tasks_monitor import task_set_timer_dashboard, task_set_timer_user, task_set_timer_encode, task_set_timer_export, \
    task_print_value


class SnippetSerializer(serializers.Serializer):
    values = serializers.CharField(write_only=True)

def is_running(key):
    t = cache.get('monitor_node_' + key)
    if t is None:
        return False
    d = timezone.now() - t
    _ = d.total_seconds()
    if _ > 10:
        return False
    else:
        return True


class MonitorCeleryView(APIView):
    serializer_class = None
    permission_classes = [AllowAny]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, request, format=None):
        task_set_timer_user.delay()
        task_set_timer_dashboard.delay()
        task_set_timer_export.delay()
        task_set_timer_encode.delay()
        task_print_value.delay(value='jade')
        is_user_running = is_running('user')
        return Response(data={
            'is_user_running': is_user_running,
        }, status=status.HTTP_200_OK)



