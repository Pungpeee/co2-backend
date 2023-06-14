import ast

from config.models import Config
from log.models import Log


def get_code(content_type):
    return '%s.%s' % (content_type.app_label, content_type.model)

def fcm_notification_config():
    config_setting = {}
    notification_config = Config.pull_value('notification-client-list')
    if isinstance(notification_config, str):
        # "{Dict: 'data_in_dict'}" -> {Dict: 'data_in_dict'}
        value_text = ast.literal_eval(notification_config)
    else:
        # {Dict: 'data_in_dict'}
        value_text = notification_config

    if 'app_name' in value_text and 'setting' in value_text and 'service' in value_text:
        key_set = value_text['app_name']
        config_setting[key_set] = {}
        config_setting[key_set].update({
            'setting': value_text['settings'],
            'service': value_text['service'],
        })
    else:
        Log.push(
            request=None,
            group='UTILS',
            code='CONFIG_NOT_COMPLETE',
            account=None,
            status='Update config_setting fail',
            status_code='500',
            payload=value_text,
            note='utils/content.py device_notification: Wrong Format'
        )
    return config_setting