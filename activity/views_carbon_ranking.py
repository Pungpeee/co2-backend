from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from .serializers import CarbonSavingRankSerializer
from .models import CarbonActivity
from account.models import Account
from django.db.models import Window, F, Sum
from django.db.models.functions import DenseRank
from utils.advanced_filters.emoji_filter import SearchFilter


class CarbonSavingRankView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = CarbonActivity.objects.all()
    permission_classes = [AllowAny]
    serializer_class = CarbonSavingRankSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filterset_fields = ['type', 'coin']
    search_fields = ['activity_code', 'activity_name', 'activity_details', 'coin']

    action_serializers = {
        'list': CarbonSavingRankSerializer,
    }

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = CarbonActivity.objects.filter(transaction__method=4, transaction__status=2)
        key_filter_list = ['activity']
        if any(key in self.request.query_params for key in key_filter_list):
            print(self.request.query_params)
            queryset = queryset

        return queryset

    def list(self, request, *args, **kwargs):
        activity_types = [
            'dining',
            'shopping',
            'transportation',
            'recycle',
            'foresting',
            'others',
            'all'
        ]
        result = {}
        for activity_type in activity_types:
            if activity_type == 'dining':
                queryset = CarbonActivity.objects.filter(type=1)
            elif activity_type == 'shopping':
                queryset = CarbonActivity.objects.filter(type=2)
            elif activity_type == 'transportation':
                queryset = CarbonActivity.objects.filter(type=3)
            elif activity_type == 'recycle':
                queryset = CarbonActivity.objects.filter(type=4)
            elif activity_type == 'foresting':
                queryset = CarbonActivity.objects.filter(type=5)
            elif activity_type == 'others':
                queryset = CarbonActivity.objects.filter(type=6)
            else:
                queryset = CarbonActivity.objects.all()

            rank_list = queryset.values(
                'transaction__account_id',
                'transaction__account__first_name',
                'transaction__account__last_name',
                'transaction__account__email',
                'transaction__account__image',
            ).annotate(
                total_carbon_saving=Sum('carbon_saving'),
                rank=Window(
                    expression=DenseRank(),
                    order_by=[
                        F('total_carbon_saving').desc()
                    ]
                )
            ).order_by('rank')

            rank_result = list(rank_list[:10])

            serializer = self.serializer_class(rank_result, many=True)
            result[activity_type] = serializer.data
        return Response(result)

    @action(methods=['GET'], detail=False, url_path='myRank')
    def my_rank(self, request, *args, **kwargs):
        activity_types = [
            'dining',
            'shopping',
            'transportation',
            'recycle',
            'foresting',
            'others',
            'all'
        ]
        result = {}
        for activity_type in activity_types:
            if activity_type == 'dining':
                queryset = CarbonActivity.objects.filter(type=1)
            elif activity_type == 'shopping':
                queryset = CarbonActivity.objects.filter(type=2)
            elif activity_type == 'transportation':
                queryset = CarbonActivity.objects.filter(type=3)
            elif activity_type == 'recycle':
                queryset = CarbonActivity.objects.filter(type=4)
            elif activity_type == 'foresting':
                queryset = CarbonActivity.objects.filter(type=5)
            elif activity_type == 'others':
                queryset = CarbonActivity.objects.filter(type=6)
            else:
                queryset = CarbonActivity.objects.all()
            rank_list = queryset.values(
                'transaction__account_id',
                'transaction__account__first_name',
                'transaction__account__last_name',
                'transaction__account__email',
                'transaction__account__image',
            ).annotate(
                total_carbon_saving=Sum('carbon_saving'),
                rank=Window(
                    expression=DenseRank(),
                    order_by=[
                        F('total_carbon_saving').desc()
                    ]
                )
            ).order_by('rank')
            try:
                my_rank = rank_list.get(transaction__account_id=request.user.id)
                result[activity_type] = self.get_serializer(my_rank).data
            except CarbonActivity.DoesNotExist:
                try:
                    first_name = request.user.first_name
                except Exception as e:
                    first_name = ''
                try:
                    last_name = request.user.last_name
                except Exception as e:
                    last_name = ''
                try:
                    email = request.user.email
                except Exception as e:
                    email = ''
                try:
                    image = request.user.image
                except Exception as e:
                    image = ''
                result[activity_type] = {
                    "full_name": f'{first_name} {last_name}',
                    "email": email,
                    "image": image,
                    "total_carbon_saving": 0,
                    "rank": Account.objects.all().count()
                }
            except Exception as e:
                result[activity_type] = {}
        return Response(result)