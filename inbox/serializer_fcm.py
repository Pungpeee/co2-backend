from rest_framework import serializers

from inbox.models import Inbox
# from news_update.models import NewsUpdate
from utils.content import get_code


class FCMInboxSerializer(serializers.ModelSerializer):
    content_type_name = serializers.SerializerMethodField()
    content_name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()

    class Meta:
        model = Inbox
        fields = (
            'content_id',
            'content_type',
            'content_type_name',
            'content_name',
            'image',
            'code'
        )

    def get_content_type_name(self, inbox):
        return '%s.%s' % (inbox.content_type.app_label, inbox.content_type.model)

    def get_content_name(self, inbox):
        # from news_update.models import NewsUpdate
        #
        # if inbox.type == 2:
        #     news = NewsUpdate.objects.filter(id=inbox.content_id).first()
        #     if news:
        #         return getattr(news, 'name', '')
        #     else:
        #         return ''
        if inbox.type == 1:
            return inbox.title

    def get_image(self, inbox):
        # if inbox.type == 2:
        #
        #     news_update = NewsUpdate.objects.get(id=inbox.content_id)
        #     if news_update:
        #         gallery = news_update.gallery_set.filter(is_cover=True).first()
        #         if gallery:
        #             if not gallery.image:
        #                 return ''
        #             else:
        #                 return gallery.image.url
        #         else:
        #             return ''
        if inbox.type == 1:
            if not inbox.image:
                return ''
            else:
                return inbox.image.url

    def get_code(self, inbox):
        if inbox.content_type is None:
            return ''
        else:
            return get_code(inbox.content_type)