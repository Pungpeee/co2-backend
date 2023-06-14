import os

from django.contrib import admin

from .caches import cache_config_last_update_web_delete, cache_config_result_web_delete, \
    cache_config_result_dashboard_delete, cache_config_last_update_dashboard_delete
from .models import Config, Locale
# from .tasks import google_analytics_task

@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('code', 'app', 'name', 'is_web', 'is_dashboard', 'type', 'value', 'sort', 'datetime_update')
    list_filter = ('app',)
    search_fields = ['code']
    # readonly_fields = ['is_web', 'is_dashboard', 'type']

    def save_model(self, request, obj, form, change):
        if obj.code == 'config-favicon':
            _path = os.path.join(os.path.split(obj.image.path)[0], 'favicon.ico')
            with open(_path, 'wb+') as destination:
                for chunk in obj.image.chunks():
                    destination.write(chunk)

            _path = os.path.join(os.path.split(obj.image.path)[0], 'favicon.png')
            with open(_path, 'wb+') as destination:
                for chunk in obj.image.chunks():
                    destination.write(chunk)

        if obj.code == 'config-apple-app-site-association':
            if bool(obj.image):
                dir_name, file_name = os.path.split(obj.image.path)
                path = os.path.join(dir_name, 'config/image', file_name)
                if os.path.exists(path):
                    os.remove(path)

        super().save_model(request, obj, form, change)
        Config.cache_delete(obj.code)

@admin.register(Locale)
class LocaleAdmin(admin.ModelAdmin):
    list_display = ('config', 'code', 'value')
