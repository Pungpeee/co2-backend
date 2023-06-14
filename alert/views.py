from asgiref.sync import AsyncToSync
from channels.layers import get_channel_layer

from alert.serializers_import_history import AlertImportHistoryEventSerializer


def broadcast_import_history_progress(alert, is_new=False, percent=None):
    if alert.module_name:
        try:
            module, function = alert.module_name.replace(' ', '_').replace(')', '').split('_(')
            module_name = '%s__%s' % (module, function)
        except:
            module_name = alert.module_name.replace(' ', '_').replace(')', '')
        broadcast_group_name = 'import_history'
        individual_group_name = 'import_history_%s_%s' % (alert.account.id, module_name.lower())
        channel_layer = get_channel_layer()
        data = AlertImportHistoryEventSerializer(alert).data
        data['is_new'] = is_new

        if percent:
            data['percent'] = int(percent)

        AsyncToSync(channel_layer.group_send)(broadcast_group_name, {'type': 'send_event',
                                                                     'data': {'event': 'import_history', 'data': data}})

        AsyncToSync(channel_layer.group_send)(individual_group_name, {'type': 'send_event',
                                                                      'data': {'event': 'import_history', 'data': data}})