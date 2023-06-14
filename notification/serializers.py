from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.utils.module_loading import import_string
from fcm_django.models import FCMDevice
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer, ModelSerializer
from inbox.models import Inbox, Count, Read
from utils.content import get_code


def get_inbox_content_serializer(content_type, content_id):
    try:
        if content_type == settings.CONTENT_TYPE('event.session'):
            serializer_class = import_string('%s.serializers_notification.SessionNotificationSerializer' % content_type.app_label)
        else:
            serializer_class = import_string('%s.serializers_notification.NotificationSerializer' % content_type.app_label)
    except:
        return {}

    model = content_type.model_class()
    content = model.pull(content_id)
    if content:
        return serializer_class(content).data
    else:
        return {}


class DeviceSerializerMixin(ModelSerializer):
    class Meta:
        fields = (
            "id", "name", "registration_id", "device_id", "active",
            "date_created", "type"
        )
        read_only_fields = ("id", "date_created",)

        extra_kwargs = {"active": {"default": True}}


class UniqueRegistrationSerializerMixin(Serializer):
    def validate(self, attrs):
        devices = None
        primary_key = None
        request_method = None

        if self.initial_data.get("registration_id", None):
            if self.instance:
                request_method = "update"
                primary_key = self.instance.id
            else:
                request_method = "create"
        else:
            if self.context["request"].method in ["PUT", "PATCH"]:
                request_method = "update"
                primary_key = attrs["id"]
            elif self.context["request"].method == "POST":
                request_method = "create"

        device = self.Meta.model
        # if request authenticated, unique together with registration_id and
        # user
        user = self.context['request'].user
        if request_method == "update":
            if user is not None:
                devices = device.objects.filter(
                    registration_id=attrs["registration_id"]) \
                    .exclude(id=primary_key)
                if (attrs["active"]):
                    devices.filter(~Q(user=user)).update(active=False)
                devices = devices.filter(user=user)
            else:
                devices = device.objects.filter(
                    registration_id=attrs["registration_id"]) \
                    .exclude(id=primary_key)
        elif request_method == "create":
            if user is not None:
                devices = device.objects.filter(
                    registration_id=attrs["registration_id"])
                devices.filter(~Q(user=user)).update(active=False)
                devices = devices.filter(user=user)
            else:
                devices = device.objects.filter(
                    registration_id=attrs["registration_id"])

        if devices:
            raise ValidationError(
                {'registration_id': 'This field must be unique.'})
        return attrs


class FCMDeviceSerializer(ModelSerializer, UniqueRegistrationSerializerMixin):
    class Meta(DeviceSerializerMixin.Meta):
        model = FCMDevice

        extra_kwargs = {"id": {"read_only": False, "required": False}}


class CountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Count
        fields = ('count',)


class ReadCountSerializer(serializers.Serializer):
    count = serializers.ReadOnlyField()

    class Meta:
        model = Count
        fields = ('count',)


class InboxReadSerializer(serializers.Serializer):
    id_list = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    channel = serializers.IntegerField(min_value=1, max_value=3, default=3)

    def save(self, **kwargs):
        validated_data = dict(
            list(self.validated_data.items()) + list(kwargs.items())
        )
        return self.create(validated_data)

    def create(self, validated_data):
        inbox_id_list = validated_data.get('id_list', [])
        request = self.context.get('request')
        account = request.user
        read_list = []
        for inbox_id in inbox_id_list:
            read_list.append(Read(inbox_id=inbox_id, account=account))
        Read.objects.bulk_create(read_list)
        return Inbox.objects.filter(member__account=account)


class InboxSerializer(serializers.ModelSerializer):
    type_display = serializers.SerializerMethodField()

    content = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()

    datetime_create = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()

    class Meta:
        model = Inbox
        fields = (
            'id',
            'title',

            'type',
            'type_display',

            'content',
            'is_read',

            'datetime_create',
            'code',
        )

    def get_type_display(self, inbox):
        return inbox.get_type_display()

    def get_content(self, inbox):
        return get_inbox_content_serializer(inbox.content_type, inbox.content_id)

    def get_is_read(self, inbox):
        return inbox.is_read

    def get_datetime_create(self, inbox):
        return timezone.localtime(inbox.datetime_create).isoformat()

    def get_code(self, inbox):
        if inbox.content_type:
            return get_code(content_type=inbox.content_type)
        else:
            return None
