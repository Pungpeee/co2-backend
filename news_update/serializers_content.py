from django.conf import settings
from rest_framework import serializers

from account.dashboard.serializers import AccountMiniSerializer
from news_update.dashboard.serializers_gallery import GallerySerializer
from news_update.models import NewsUpdate
from analytic.models import ContentViewLog
from account.models import Account


class NewsUpdateDetailSerializer(serializers.ModelSerializer):
    count_view = serializers.SerializerMethodField()
    image_list = serializers.SerializerMethodField()
    create_by = AccountMiniSerializer(source='account')
    update_by = AccountMiniSerializer()

    class Meta:
        model = NewsUpdate
        fields = ('id',
                  'name',
                  'image_list',
                  'is_pin',
                  'is_notification',
                  'is_display',
                  'count_view',
                  'count_notification',
                  'create_by',
                  'update_by',
                  'datetime_create',
                  'datetime_update',
                  )

    def get_image_list(self, announcement):
        queryset = announcement.gallery_set.all()
        return GallerySerializer(instance=queryset, many=True).data

    def get_count_view(self, announcement):
        content_type = settings.CONTENT_TYPE('news_update.newsupdate')
        user_account_id_list = Account.objects.exclude(type=1).values_list('id', flat=True)
        content_view_log = ContentViewLog.objects.filter(content_id=announcement.id,
                                                         content_type=content_type,
                                                         account_id__in=user_account_id_list)
        count_view = content_view_log.count() if content_view_log else 0
        return count_view
