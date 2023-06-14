import json

from django.contrib.admin.utils import NestedObjects
from django.core import serializers


def dependency(_):
    collector = NestedObjects(using='default')
    collector.collect([_])
    object_list = collector.nested()
    print(object_list)
    data = []
    for object in object_list:
        if isinstance(object, list):
            for o in object:
                data.append(json.loads(serializers.serialize('json', [o])))
        else:
            data.append(json.loads(serializers.serialize('json', [object])))

    return data
