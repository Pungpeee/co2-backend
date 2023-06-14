from rest_framework.response import Response
from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum

from .models import CarbonActivity, Transaction
from .serializers import ActivitySerializer


class OverallView(viewsets.GenericViewSet):
    queryset = CarbonActivity.objects.all()
    permission_classes = (AllowAny,)
    allow_redirects = True
    serializer_class = ActivitySerializer

    @action(methods=['GET'], detail=False, url_path='carbon')
    def carbon(self, request, *args, **kwargs):
        sum_carbon = self.queryset.aggregate(Sum('carbon_saving'), Sum('values'))
        data = {
            'carbon_removed': round(sum_carbon.get('carbon_saving__sum', 0), 4),
            'transactions': Transaction.objects.all().count(),
            'green_product_purchased': round(sum_carbon.get('values__sum', 0), 4)
        }
        return Response(data=data)
