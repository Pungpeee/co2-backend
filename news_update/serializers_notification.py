from rest_framework import serializers

from news_update.models import NewsUpdate


class NotificationSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = NewsUpdate
        fields = ('id', 'name', 'image')

    def get_image(self, news_update):
        gallery = news_update.gallery_set.filter(is_cover=True).first()
        if gallery:
            if not gallery.image:
                return ''
            else:
                return gallery.image.url
        else:
            return ''
