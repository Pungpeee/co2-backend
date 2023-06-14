from django.core.management.base import BaseCommand

from config.data import CONFIG_DICT
from config.data_account import CONFIG_DICT as CONFIG_DICT_ACCOUNT
from config.models import Config


class Command(BaseCommand):
    def handle(self, *args, **options):
        Config.init()
        self.stdout.write(self.style.SUCCESS('Config Init Successfully.'))
        self.stdout.write(self.style.WARNING('Config Init Successfully.'))
        config_dict = CONFIG_DICT.copy()
        config_dict.update(CONFIG_DICT_ACCOUNT)
        for key, data in config_dict.items():
            if 'migrate_if_value' in data:
                old_value = Config.pull_value(key)
                if old_value == data['migrate_if_value']:
                    print('%s => change. from %s to %s' % (key, old_value, data['value']))
                    Config.set_value(key, data['value'])
                else:
                    print('%s => ok.' % key)
