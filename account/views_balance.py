import json

import requests
from django.conf import settings
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from log.models import Log
from transaction.models import Transaction
from transaction.serializers import TransactionBalance
from utils.ip import get_client_ip
from .models import Account
from .serializers import AccountBalanceSerializer


class AccountBalanceView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Account.objects.none()
    serializer_class = AccountBalanceSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    permission_classes_action = {
        'list': [IsAuthenticated]
    }

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Account.objects.filter(id=self.request.user.id)
        else:
            return self.queryset

    def get_object(self, queryset=None):
        account = Account.objects.filter(pk=self.request.user.id).first()
        return account

    def get_serializer_context(self):
        return {
            "request": self.request
        }

    def list(self, request, *args, **kwargs):
        account = Account.objects.filter(id=self.request.user.id).first()

        url = settings.CO2_CHAIN_API_URL + "wallet/get_balance"
        _request = dict()
        if not account or not account.sol_public_key or not account.bsc_public_key:
            if isinstance(request, dict):
                _request = json.dumps(request)
            elif isinstance(request, str):
                _request = str(request)

            Log.push(request, 'ACCOUNT',
                     'CHECK_BALANCE', account,
                     'This Account try to check wallet with out wallet information',
                     status.HTTP_200_OK,
                     note='{ip:%s, request:%s}' % (get_client_ip(request), _request))
            return Response(data={'Have something wrong with Account Wallet'},
                            status=status.HTTP_404_NOT_FOUND)

        payload = json.dumps({
            "account_id": account.id,
        })

        if not settings.CO2_CHAIN_API_KEY:
            Log.push(
                request,
                'ACCOUNT_WALLET',
                'VEKIN',
                account,
                'API KEY WALLET NOT SETTING',
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        headers = {
            'authorization': settings.CO2_CHAIN_API_KEY,
            'Content-Type': 'application/json'
        }

        # response = requests.request("POST", url, headers=headers, data=payload)
        # if response.status_code != 200 and response.status_code != 201:
        #     #TODO : Transaction Token check here @jade
        #     Log.push(request, 'ACCOUNT',
        #              'CHECK_BALANCE', account, 'Have something wrong with API check balance wallet',
        #              status.HTTP_200_OK, payload=response.__dict__)
        #     return Response(data={'Have something wrong with API check balance wallet'}, status=status.HTTP_400_BAD_REQUEST)

        # wallet_data = json.loads(response.text)
        # if not wallet_data or not wallet_data.get('sol', None) or not wallet_data.get('bsc', None):
        #     Log.push(request, 'ACCOUNT',
        #              'CHECK_BALANCE', account, 'Have something wrong with API check balance wallet',
        #              status.HTTP_200_OK, payload=response.__dict__)
        #     return Response(data={'Not found address'}, status=status.HTTP_404_NOT_FOUND)

        # if wallet_data:
        #     sol_wallet = wallet_data.get('sol', None)
        #     if sol_wallet.get('address', None) != account.sol_public_key:
        #         Log.push(request, 'ACCOUNT',
        #                  'WALLET_NOT_MATCH', account, 'wallet address in django not same with solona wallet server',
        #                  status.HTTP_200_OK, payload=response.__dict__)
        #         return Response(
        #             data={'Wallet address not match with account, Please Contact admin'},
        #             status=status.HTTP_406_NOT_ACCEPTABLE
        #         )
        # sol_wallet = wallet_data.get('sol', None)

        # if not sol_wallet or not 'balance' in sol_wallet:
        #     Log.push(request, 'ACCOUNT',
        #              'SOL_BALANCE_NOT_FOUND', account, 'Have something wrong with API check balance wallet',
        #              status.HTTP_200_OK, payload=response.__dict__)
        #     return Response(data={'Balance not found'}, status=status.HTTP_404_NOT_FOUND)

        response = self.get_serializer(account).data

        transaction_query = Transaction.objects.filter(account_id=account.id)
        transaction_list = TransactionBalance(transaction_query, many=True).data
        # response.update({
        #     "wallet": wallet_data if isinstance(wallet_data, dict) else {},
        #     "transaction_list": transaction_list if transaction_list else []
        # })

        # Mockup Response
        # TODO: Revise later
        response.update({
            "wallet": {
                "sol": {
                    "chain": "SOL",
                    "address": account.sol_public_key,
                    "coin": "CERO",
                    "balance": 0
                },
                "bsc": {
                    "chain": "BSC",
                    "address": account.bsc_public_key,
                    "coin": "CERO",
                    "balance": 0
                }
            },
            "transaction_list": transaction_list if transaction_list else []
        })

        if not account:
            return Response(data={'Details : Have no this account in system'}, status=status.HTTP_404_NOT_FOUND)
        return Response(data=response)
