from django.contrib import admin

from news_update.models import NewsUpdate, Gallery, NewsUpdateLog


@admin.register(NewsUpdate)
class NewsUpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_display', 'is_pin', 'is_notification', 'sort')


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('id', 'news_update', 'is_cover')


@admin.register(NewsUpdateLog)
class NewsUpdateLog(admin.ModelAdmin):
    list_display = ('id', 'account', 'news_update', 'is_read')
