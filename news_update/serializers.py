from django.conf import settings
from rest_framework import serializers

from analytic.models import ContentView
from news_update.caches import cached_news_update_cover
from news_update.models import NewsUpdate, Gallery


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ('image',)


class NewsUpdateDetailSerializer(serializers.ModelSerializer):
    count_view = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = NewsUpdate
        fields = ('id',
                  'name',
                  'desc',
                  'is_pin',
                  'is_notification',
                  'count_view',
                  'datetime_create',
                  'is_read',
                  'datetime_update')

    def get_image_list(self, news_update):
        response = []
        gallery_list = news_update.gallery_set.all()
        for gallery in gallery_list:
            response.append({'image': gallery.image.url if gallery.image else None})
        return response

    def get_count_view(self, news_update):
        from analytic.models import ContentView
        content_type = settings.CONTENT_TYPE('news_update.newsupdate')
        return ContentView.pull_count(content_type, news_update.id)

    def get_is_read(self, news_update):
        request = self.context['request']
        account = request.user
        is_read = news_update.is_read(account)
        if not is_read:
            content_type = settings.CONTENT_TYPE('news_update.newsupdate')
            ContentView.push(request, content_type, news_update.id)
        return is_read

    def to_representation(self, news_update):
        data = super().to_representation(news_update)
        response = []
        image_url = None
        gallery_list = news_update.gallery_set.all()
        for gallery in gallery_list:
            if image_url is None:
                image_url = gallery.image.url if gallery.image else None
            response.append({'image': gallery.image.url if gallery.image else None})
        data.update({
            'image': image_url,
            'image_list': response
        })
        return data


class NewsUpdateListSerializer(serializers.ModelSerializer):
    image_list = serializers.SerializerMethodField()
    count_view = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = NewsUpdate
        fields = ('id',
                  'name',
                  'image_list',
                  'count_view',
                  'is_read',
                  'datetime_update')

    def get_image_list(self, news_update):
        response = []
        gallery_list = news_update.gallery_set.all()
        for gallery in gallery_list:
            response.append({'image': gallery.image.url if gallery.image else None})
        return response

    def get_count_view(self, news_update):
        from analytic.models import ContentView
        content_type = settings.CONTENT_TYPE('news_update.newsupdate')
        return ContentView.pull_count(content_type, news_update.id)

    def get_is_read(self, news_update):
        request = self.context['request']
        return news_update.is_read(request.user)


class NewsUpdateHomeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    account = serializers.SerializerMethodField()

    class Meta:
        model = NewsUpdate
        fields = (
            'id',
            'account',
            'image',
            'name',
            'short_desc',
            'datetime_update'
        )

    def get_account(self, obj):
        return obj.account.username if obj.account else '-'

    def get_image(self, news_update):
        gallery = cached_news_update_cover(news_update.id)
        return gallery.image.url if gallery and gallery.image else None
