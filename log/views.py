import json

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

import alert
from alert.models import Alert
from alert.serializers import AlertSerializer
from log.models import Log
from log.serializers import MiniLogSerializer, LogSerializer
from rest_framework.permissions import AllowAny


class LogDeviceView(viewsets.GenericViewSet):
    queryset = Log.objects.all()
    serializer_class = MiniLogSerializer
    permission_classes = (AllowAny,)

    app = 'log'
    model = 'log'

    def create(self, request, *args, **kwargs):
        serializer = MiniLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        log = Log.objects.create(
            group='EXTERNAL_LOG',
            code='DEVICE_EXTERNAL_LOG',
            payload=data['payload'],
            status='This data sent from external device',
            status_code=status.HTTP_201_CREATED
        )
        result = MiniLogSerializer(log).data
        return Response(result, status=status.HTTP_201_CREATED)


    def list(self, request, *args, **kwargs):
        queryset = Log.objects.filter(group='EXTERNAL_LOG', code='DEVICE_EXTERNAL_LOG')
        serializer = LogSerializer(queryset, many=True)
        return Response(serializer.data)


    @action(methods=['GET'], detail=False, url_path='test_task_1')
    def test_task_1(self, request, *args, **kwargs):
        from log.test_tasks import test_task, add

        alert = Alert.objects.create(
            account=request.user,
            code='log.test_tasks.1',
            json_kwargs=json.dumps(kwargs, indent=2),
            action_type=3,
            status=1
        )

        task_result = test_task.delay('jade', alert.id)
        alert.set_task_id(task_result.id)
        return Response(AlertSerializer(alert).data)

    @action(methods=['GET'], detail=False, url_path='test_task_2')
    def test_task_2(self, request, *args, **kwargs):
        from log.test_tasks import test_task, add

        alert = Alert.objects.create(
            account=request.user,
            code='log.test_tasks.2',
            json_kwargs=json.dumps(kwargs, indent=2),
            status=1
        )

        task_result = add.delay(1,2, alert.id)
        alert.set_task_id(task_result.id)
        return Response(AlertSerializer(alert).data)



