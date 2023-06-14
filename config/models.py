import json

from django.conf import settings
from django.core.cache import cache
from django.db import models

class Config(models.Model):
    TYPE_CHOICES = (
        (1, 'Boolean'),
        (2, 'String'),
        (3, 'Integer'),
        (4, 'Float'),
        (5, 'Text'),
        (6, 'Choices'),
        (7, 'Color'),
        (8, 'Image'),
        (9, 'List'),
        (10, 'JSON'),
        (11, 'Function'),
    )

    name = models.CharField(max_length=120)
    app = models.CharField(max_length=24, db_index=True)
    code = models.CharField(max_length=48, db_index=True, unique=True)
    desc = models.TextField(blank=True)

    is_web = models.BooleanField(default=False)
    is_dashboard = models.BooleanField(default=False)

    type = models.IntegerField(choices=TYPE_CHOICES)

    value = models.CharField(max_length=255, blank=True)
    value_text = models.TextField(blank=True)

    image = models.FileField(upload_to='config/image/', blank=True, null=True)

    sort = models.IntegerField(db_index=True, default=0)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ['sort']

    def __str__(self):
        return self.code

    @staticmethod
    def pull(code):
        from .caches import cache_config
        return cache_config(code)

    @staticmethod
    def cache_delete(code):
        from .caches import cache_config_delete, cache_config_tag_type_delete
        cache_config_delete(code)
        if code in settings.CACHED_CONFIG and settings.IS_ENABLE_CONFIG_SETTINGS:
            del settings.CACHED_CONFIG[code]

        cache_config_tag_type_delete(code)

    @staticmethod
    def pull_value(code, is_force=False):
        if code in settings.CACHED_CONFIG and not settings.TESTING and settings.IS_ENABLE_CONFIG_SETTINGS and not is_force:
            config = settings.CACHED_CONFIG[code]
        else:
            config = Config.pull(code)
            settings.CACHED_CONFIG[code] = config

        if config:
            return config.get_value()
        else:
            return None

    @staticmethod
    def init_code(code):
        from .data import CONFIG_DICT
        from .data_account import CONFIG_DICT as CONFIG_DICT_ACCOUNT
        if code in CONFIG_DICT:
            return Config.init_push(code, CONFIG_DICT[code])
        elif code in CONFIG_DICT_ACCOUNT:
            return Config.init_push(code, CONFIG_DICT_ACCOUNT[code])
        else:
            return None

    @staticmethod
    def pull_datetime_update_web():
        from .caches import cache_config_last_update_web
        return cache_config_last_update_web()

    @staticmethod
    def pull_datetime_update_dashboard():
        from .caches import cache_config_last_update_dashboard
        return cache_config_last_update_dashboard()

    @staticmethod
    def pull_dict(code):
        config = Config.pull(code)
        response = {
            config.code: {
                'app': config.app,
                'type': config.get_type_display(),
                'value': config.value,
                'value_text': config.value_text,
                'image': config.image.url if config.image else None,
                'sort': config.sort
            }
        }
        return response

    @staticmethod
    def get_feature():
        app_list = set(Config.objects.values_list('app', flat=True).distinct())
        dict_list = {}
        for app in app_list:
            config = Config.check_config(Config.config_list(app))
            if config:
                dict_list[app] = config
        return dict_list

    @staticmethod
    def check_config(code_dict):
        dict = {}
        if code_dict:
            for code in code_dict:
                if code == 'default':
                    dict['value'] = Config.pull_status_setup(*code_dict[code])
                else:
                    try:
                        dict['other']
                    except:
                        dict['other'] = []
                    dict['other'].append(
                        {
                            'name': code,
                            'value': Config.pull_status_setup(*code_dict[code])
                        }
                    )
        return dict

    @staticmethod
    def pull_status_setup(*argv):
        status = True
        for item in argv:
            status = status and bool(int(Config.objects.get(code=item).value))
        return status

    @staticmethod
    def set_value(code, value):
        config = Config.pull(code)
        if config:
            if config.type in [5, 10]:
                if type(value) == dict:
                    value = json.dumps(value, indent=2)
                config.value_text = value
            else:
                config.value = value
            config.save(update_fields=['value', 'value_text', 'datetime_update'])
            Config.cache_delete(code)
            if code in settings.CACHED_CONFIG:
                del settings.CACHED_CONFIG[code]

    @staticmethod
    def init_push(key, data):
        import json
        if 'value' in data:
            value = data['value']
            if data['type'] == 1:
                if value:
                    value = 1
                else:
                    value = 0
        else:
            value = ''
        if 'value_text' in data:
            if data['type'] == 10:
                value_text = json.dumps(data['value_text'], indent=2)
            else:
                value_text = data['value_text']
        else:
            value_text = ''
        if 'image' in data:
            image = data['image']
        else:
            image = None

        return Config.objects.create(
            name=key,
            app=data['app'],
            code=key,
            is_web=data['is_web'],
            is_dashboard=data['is_dashboard'],
            type=data['type'],
            value=value,
            value_text=value_text,
            image=image,
            sort=data['sort']
        )

    @staticmethod
    def fake_web_update():
        config = Config.objects.filter(is_web=True).first()
        if config:
            config.save(update_fields=['datetime_update'])

    @staticmethod
    def init_push(key, data):
        import json
        if 'value' in data:
            value = data['value']
            if data['type'] == 1:
                if value:
                    value = 1
                else:
                    value = 0
        else:
            value = ''
        if 'value_text' in data:
            if data['type'] == 10:
                value_text = json.dumps(data['value_text'], indent=2)
            else:
                value_text = data['value_text']
        else:
            value_text = ''
        if 'image' in data:
            image = data['image']
        else:
            image = None

        return Config.objects.create(
            name=key,
            app=data['app'],
            code=key,
            is_web=data['is_web'],
            is_dashboard=data['is_dashboard'],
            type=data['type'],
            value=value,
            value_text=value_text,
            image=image,
            sort=data['sort']
        )

    @staticmethod
    def update_config_file():
        from utils.config import generate_config_file
        import os
        path = os.path.join(settings.BASE_DIR, 'media', 'config')
        os.makedirs(path, exist_ok=True)
        file = open(path + '/config.json', 'w')

        detail = generate_config_file()

        file.write(detail)
        file.close()

    @staticmethod
    def init():
        from .data import CONFIG_DICT
        from .data_account import CONFIG_DICT as CONFIG_DICT_ACCOUNT

        config_dict = CONFIG_DICT.copy()
        config_dict.update(CONFIG_DICT_ACCOUNT)

        for config in Config.objects.all():
            if config.code in config_dict:
                is_change = False
                _ = config_dict[config.code]
                for key, value in _.items():
                    if key in ['app', 'sort', 'is_web', 'is_dashboard', 'type'] and getattr(config, key) != value:
                        is_change = True
                        setattr(config, key, value)
                if is_change:
                    config.save()

                del config_dict[config.code]

        for key, data in config_dict.items():
            Config.init_push(key, data)
        key = 'config_result_web'
        cache.delete(key)

    def push_value(self, value='', value_text=''):
        import json
        self.value = value
        if type(value_text) == dict:
            value_text = json.dumps(value_text)
        self.value_text = value_text
        self.save()
        cache.set('config_%s' % self.code, self)
        settings.CACHED_CONFIG[self.code] = self
        return self

    def get_value(self):
        if self.type in [2, 6, 7]:
            return self.value
        elif self.type == 1:
            try:
                return True if int(self.value) == 1 else False
            except:
                return True if self.value == 'True' else False
        elif self.type == 3:
            return int(self.value)
        elif self.type == 4:
            return float(self.value)
        elif self.type == 5:
            return self.value_text
        elif self.type == 8:
            if self.image:
                return self.image.url
            else:
                return None
        elif self.type == 9:
            return self.value.split(',')
        elif self.type == 10:
            import json
            import ast
            try:
                return json.loads(self.value_text)
            except:
                pass
            try:
                return ast.literal_eval(self.value_text)
            except:
                return None
        elif self.type == 11:
            from .function import ConfigFunction
            return ConfigFunction.execute(self.value, self.value_text)
        else:
            return None

    def get_locale_dict(self):
        if self.type in [1, 3, 4, 7, 8]:
            return None
        else:
            result = {}
            for locale in self.locale_set.all():
                if self.type == 2:
                    _ = locale.value
                elif self.type == 5:
                    _ = locale.value_text
                elif self.type == 6:
                    _ = 'Not implement.'
                elif self.type == 9:
                    _ = 'Not implement.'
                result[locale.code] = _
            return result

    def push(self, locale_code, value):
        if self.type in [2, 5]:
            if not Locale.check_allow(locale_code):
                return
            if locale_code:
                locale = Locale.pull(self, locale_code)
                if self.type == 2:
                    locale.value = value
                elif self.type == 5:
                    locale.value_text = value
                locale.save()
            else:
                if self.type == 2:
                    self.value = value
                elif self.type == 5:
                    self.value_text = value
                self.save()
        elif self.type == 8:
            self.image = value
            self.save()
        else:
            self.value = value
            self.save()

        if 'color' in self.code:
            Config.update_color_theme()


class Locale(models.Model):
    config = models.ForeignKey(Config, on_delete=models.CASCADE)

    code = models.CharField(max_length=24, db_index=True)
    value = models.CharField(max_length=255, blank=True)
    value_text = models.TextField(blank=True)

    class Meta:
        default_permissions = ()

    @staticmethod
    def pull(config, code):
        locale = Locale.objects.filter(config=config,
                                       code=code).first()
        if locale is None:
            locale = Locale.objects.create(config=config,
                                           code=code,
                                           value=config.value,
                                           value_text=config.value_text)
        return locale

    @staticmethod
    def check_allow(code):
        _ = Config.pull_value('config-locale')
        if code in _:
            return True
        else:
            return False
