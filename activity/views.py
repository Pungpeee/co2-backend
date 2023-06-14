from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from account.models import Account
from alert.models import Alert
from transaction.transaction_activity_earn_coin_tasks import task_transaction_earn_coin
from .models import Transaction, CarbonActivity
from .serializers import ActivitySerializer, CarbonActivityCreateSerializer, ActivityRecentSerializer
from account.caches import cache_account_delete
import requests
from django.conf import settings
import json
from log.models import Log


class ActivityView(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ActivitySerializer

    permission_classes_action = {
        'list': [IsAuthenticated],
        'create': [IsAuthenticated],
    }

    action_serializers = {
        'list': ActivitySerializer,
        'create': CarbonActivityCreateSerializer
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.account = Account.objects.filter(id=request.user.id).first()
        if self.account is None:
            raise NotFound

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super().get_serializer_class()

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        transaction_id_list = list(
            Transaction.objects.filter(account_id=self.request.user.id, method=4).values_list('id', flat=True))
        if self.request.user.is_authenticated:
            return CarbonActivity.objects.filter(transaction_id__in=transaction_id_list)
        else:
            return self.queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
        else:
            response_data = self.get_serializer(queryset, many=True).data
        return Response(data=response_data)

    @action(methods=['GET'], detail=False, url_path='recent')
    def recent(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response_data = ActivityRecentSerializer(queryset, many=True).data
        return Response(data=response_data)

    @action(methods=['GET'], detail=False, url_path='carbonBalance')
    def carbon_balance(self, request, *args, **kwargs):
        activities = CarbonActivity.objects.filter(transaction__account=request.user)
        data = {
            'totalBalance': 0,
            'dining': 0,
            'shopping': 0,
            'transportation': 0,
            'recycle': 0,
            'foresting': 0,
            'others': 0
        }
        for activity in activities:
            if activity.type == 1:
                data['dining'] += activity.carbon_saving
            elif activity.type == 2:
                data['shopping'] += activity.carbon_saving
            elif activity.type == 3:
                data['transportation'] += activity.carbon_saving
            elif activity.type == 4:
                data['recycle'] += activity.carbon_saving
            elif activity.type == 5:
                data['foresting'] += activity.carbon_saving
            elif activity.type == 6:
                data['others'] += activity.carbon_saving
            data['totalBalance'] += activity.carbon_saving

        for key, value in data.items():
            data[key] = round(data[key], 6)

        return Response(data=data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data

        transaction = Transaction.objects.create(
            account_id=request.user.id,
            transaction_hash='',
            source_key='',
            desc=data.get('desc', '-'),
            paid_by=self.account.get_full_name(),
            destination_key=self.account.sol_public_key,
            values=data.get('values', 0.0),
            coin=1,
            method=4,
            status=-1,
            datetime_start=timezone.now()
        )
        activity = CarbonActivity.objects.create(
            transaction_id=transaction.id,
            type=data.get('type', 1),
            activity_code=data.get('activity_code', '-'),
            activity_name=data.get('activity_name', '-'),
            activity_details=data.get('activity_details', '-'),
            coin=1,
            desc=data.get('desc', '-'),
            values=data.get('values', 0.0),
            carbon_saving=data.get('carbon_saving', 0.0)
        )
        if not transaction or not activity:
            return Response(data={'detail': 'Can\'t create activity or transaction'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(ActivitySerializer(activity).data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False, url_path='bill')
    def bill_activity(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        try:
            old_bill = CarbonActivity.objects.filter(desc__contains=json.loads(data['desc'])['tax_inv_id'],
                                                     activity_code=data['activity_code'])
            if len(old_bill) > 0:
                return Response(data={'detail': 'This bill is already used'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(data={'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        transaction = Transaction.objects.create(
            account_id=request.user.id,
            transaction_hash='',
            source_key='',
            desc=data.get('desc', '-'),
            paid_by=self.account.get_full_name(),
            destination_key=self.account.sol_public_key,
            values=data.get('values', 0.0),
            coin=1,
            method=4,
            status=-1,
            datetime_start=timezone.now()
        )
        activity = CarbonActivity.objects.create(
            transaction_id=transaction.id,
            type=data.get('type', 1),
            activity_code=data.get('activity_code', '-'),
            activity_name=data.get('activity_name', '-'),
            activity_details=data.get('activity_details', '-'),
            coin=1,
            desc=data.get('desc', '-'),
            values=data.get('values', 0.0),
            carbon_saving=data.get('carbon_saving', 0.0)
        )
        if not transaction or not activity:
            return Response(data={'detail': 'Can\'t create activity or transaction'},
                            status=status.HTTP_400_BAD_REQUEST)

        headers = {
            'authorization': settings.CO2_CHAIN_API_KEY,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            'account_id': transaction.account.id,
            'to_address': user.sol_public_key,
            'token_name': 'CERO',
            'amount': activity.values,
            'class': activity.activity_name,
            'sub_class': activity.activity_code,
            'carbon_weight': activity.carbon_saving,
            'project_name': 'mcard'
        })
        response = requests.request(
            'POST',
            f'{settings.CO2_CHAIN_API_URL}transfer/earn_token/',
            headers=headers,
            data=payload
        )
        if response.status_code != 200:
            return Response(data={'detail': 'error while earn coin from chain', 'message': response.json()},
                            status=status.HTTP_400_BAD_REQUEST)

        Log.push(request, 'ACTIVITY', 'EARN_COIN', user, f'Earn coin success. Transaction {transaction.id} Activity {activity.id}',
                 status.HTTP_200_OK, payload=payload)

        return Response(ActivitySerializer(activity).data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False, url_path='make-bill')
    def make_bill_activity(self, request, *args, **kwargs):
        data = request.data
        user = Account.objects.get(pk=data['target_user'])

        if not request.user.is_superuser:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        transaction = Transaction.objects.create(
            account_id=data['target_user'],
            transaction_hash='',
            source_key='',
            desc=data.get('desc', '-'),
            paid_by=user.get_full_name(),
            destination_key=user.sol_public_key,
            values=data.get('values', 0.0),
            coin=1,
            method=4,
            status=-1,
            datetime_start=timezone.now()
        )
        activity = CarbonActivity.objects.create(
            transaction_id=transaction.id,
            type=data.get('type', 1),
            activity_code=data.get('activity_code', '-'),
            activity_name=data.get('activity_name', '-'),
            activity_details=data.get('activity_details', '-'),
            coin=1,
            desc=data.get('desc', '-'),
            values=data.get('values', 0.0),
            carbon_saving=data.get('carbon_saving', 0.0)
        )
        if not transaction or not activity:
            return Response(data={'detail': 'Can\'t create activity or transaction'},
                            status=status.HTTP_400_BAD_REQUEST)

        headers = {
            'authorization': settings.CO2_CHAIN_API_KEY,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            'account_id': transaction.account.id,
            'to_address': user.sol_public_key,
            'token_name': 'CERO',
            'amount': activity.values,
            'class': activity.activity_name,
            'sub_class': activity.activity_code,
            'carbon_weight': activity.carbon_saving,
            'project_name': 'mcard'
        })
        response = requests.request(
            'POST',
            f'{settings.CO2_CHAIN_API_URL}transfer/earn_token/',
            headers=headers,
            data=payload
        )
        if response.status_code != 200:
            return Response(data={'detail': 'error while earn coin from chain', 'message': response.json()},
                            status=status.HTTP_400_BAD_REQUEST)

        Log.push(request, 'ACTIVITY', 'MAKE_COIN', user, f'Make coin success for user {user.id} by {request.user.id}. Transaction {transaction.id} Activity {activity.id}',
                 status.HTTP_200_OK, payload=payload)

        return Response(ActivitySerializer(activity).data, status=status.HTTP_201_CREATED)
