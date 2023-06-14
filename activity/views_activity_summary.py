from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import ActivitySummarySerializer
from .models import CarbonActivity
from transaction.models import Transaction
from django.db.models import Sum
from operator import itemgetter
from utils.advanced_filters.emoji_filter import SearchFilter
from rest_framework.filters import OrderingFilter


class ActivitySummaryView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = CarbonActivity.objects.filter(transaction__method=4, transaction__status=2)
    permission_classes = (AllowAny,)
    serializer_class = ActivitySummarySerializer
    # filter_backends = (OrderingFilter, SearchFilter)
    # ordering_fields = ['type']
    # search_fields = ['type']
    
    action_serializers = {
        'list': ActivitySummarySerializer,
    }

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super().get_serializer_class()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = CarbonActivity.objects.filter(
                transaction__account_id=self.request.user.id,
                transaction__method=4,
                transaction__status=2
            )
        else:
            queryset = CarbonActivity.objects.filter(
                transaction__method=4,
                transaction__status=2
            )
        return queryset

    def list(self, request, *args, **kwargs):
        activity_type_dict = dict(CarbonActivity.TYPE_CHOICE)
        data_result = {}
        data_result.update({'overall_carbon_saving': 0.0, 'category': []})
        queryset = self.filter_queryset(self.get_queryset())
        activity_type_id_list = [key for key, value in activity_type_dict.items() if int(key) >= 1]
        for activity_type_id in activity_type_id_list:
            data_result['category'].append({
                "type": activity_type_id,
                "type_display": activity_type_dict[activity_type_id].replace('_', ' ').title(),
                "total_carbon_saving": 0.0
            })
        if not queryset:
            return Response(data=data_result, status=status.HTTP_200_OK)
        activity_list = [activity[0] for activity in CarbonActivity.TYPE_CHOICE if activity[0] >= 1]
        data_result.update(queryset.aggregate(overall_carbon_saving=Sum('carbon_saving')))
        data_result['category'] = list(queryset.values('type').order_by('type').annotate(total_carbon_saving=Sum('carbon_saving')))
        if len(activity_list) != len(data_result['category']):
            result = set(activity_list) ^ set([activity.get('type') for activity in data_result['category']])
            for type in result:
                data_result['category'].append({'type': type, 'total_carbon_saving': 0.0})
            data_result['category'] = sorted(data_result['category'], key=itemgetter('type'))
        query_list = []
        for instance in data_result['category']:
            query_list.append(self.get_serializer(instance).data)
        data_result['category'] = query_list
        return Response(data_result, status=status.HTTP_200_OK)
