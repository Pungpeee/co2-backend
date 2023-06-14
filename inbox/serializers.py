from datetime import date

from rest_framework import serializers

from inbox.models import Inbox, Count


class InboxSerilailizer(serializers.ModelSerializer):
    # Account
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Inbox
        fields = (
            'id',
            'body',
            'title',
            'datetime_create',
            'count_read',

            'name',
            'email',
            'image'
        )

    def get_name(self, inbox):
        if inbox.account is None:
            return "-"
        else:
            return inbox.account.get_full_name()

    def get_email(self, inbox):
        if inbox.account is None:
            return "-"
        else:
            return inbox.account.email

    def get_image(self, inbox):
        if getattr(inbox, 'image'):
            return "-"
        else:
            account = inbox.account
            if not account:
                return "-"
            else:
                return account.image.url if account.image else '-'


class InboxReadSerializer(serializers.Serializer):
    id_list = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    # channel = serializers.IntegerField(min_value=1, max_value=3, default=3)

    def save(self, **kwargs):
        validated_data = dict(
            list(self.validated_data.items()) + list(kwargs.items())
        )
        return self.create(validated_data)

    def create(self, validated_data):
        id_list = validated_data.get('id_list')
        # channel = validated_data.get('channel')

        inbox_list = Inbox.objects.filter(id__in=id_list, status=1)

        request = self.context.get('request')
        account = request.user
        for inbox in inbox_list:
            inbox.count_read += 1
            if not inbox.read_set.filter(account=account).exists():
                inbox.read_set.create(account=account)
            # if not inbox.read_set.filter(account=account, channel=channel).exists():
            #     inbox.read_set.create(account=account, channel=channel)
            inbox.save(update_fields=['count_read', 'datetime_update'])
        return inbox_list


class CountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Count
        fields = ('count',)


class ReadCountSerializer(serializers.Serializer):
    count = serializers.ReadOnlyField()

    class Meta:
        model = Count
        fields = ('count',)
