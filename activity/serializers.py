from rest_framework import serializers

from activity.models import CarbonActivity
from config.models import Config
from transaction.models import Transaction
from card.models import Card
from account.models import Account
import json


class ActivitySerializer(serializers.ModelSerializer):
    desc = serializers.SerializerMethodField()

    class Meta:
        model = CarbonActivity
        fields = "__all__"

    def to_representation(self, carbon_activity):
        data = super().to_representation(carbon_activity)
        type_status = carbon_activity.get_type_display()
        data.update({
            'type_status': type_status,
        })
        return data

    def get_desc(self, activity):
        try:
            return json.loads(activity.desc)
        except Exception as e:
            return {}


class ActivityRecentSerializer(serializers.ModelSerializer):
    desc = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    class Meta:
        model = CarbonActivity
        fields = "__all__"

    def to_representation(self, carbon_activity):
        data = super().to_representation(carbon_activity)
        type_status = carbon_activity.get_type_display()
        data.update({
            'type_status': type_status,
        })
        return data

    def get_desc(self, activity):
        try:
            return json.loads(activity.desc)
        except Exception as e:
            return {}

    def get_title(self, activity):
        try:
            desc = json.loads(activity.desc)
        except Exception as e:
            desc = {}
        activity_type = 'Other Activity'
        if activity.type == 1:
            activity_type = 'Dining Activity'
        elif activity.type == 2:
            activity_type = f'Shopping Activity Invoice: {desc.get("tax_inv_id", "")}'
        elif activity.type == 3:
            activity_type = 'Transportation Activity'
        elif activity.type == 4:
            activity_type = 'Recycle Activity'
        elif activity.type == 5:
            activity_type = f'Foresting {desc.get("tree_name", "")} Activity'
        return f'Earn from {activity_type}'


class CarbonActivityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonActivity
        fields = (
            'id',
            'type',
            'activity_code',
            'activity_name',
            'activity_details',
            'desc',
            'carbon_saving',
            'values'
        )


class ActivitySummarySerializer(serializers.Serializer):
    type = serializers.IntegerField()
    total_carbon_saving = serializers.FloatField()

    def to_representation(self, instance):
        data_dict_type = dict(CarbonActivity.TYPE_CHOICE)
        data = dict(super().to_representation(instance))
        # to arrange data display
        carbon_saving = data.get('total_carbon_saving')
        data.popitem()
        data['type_display'] = data_dict_type[int(data.get('type'))].replace('_', ' ').title()
        data['total_carbon_saving'] = carbon_saving
        return data


class CarbonSavingRankSerializer(serializers.Serializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    total_carbon_saving = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()

    class Meta:
        model = CarbonActivity
        fields = ['rank', 'full_name', 'total_carbon_saving']
    
    def get_full_name(self, instance):
        try:
            first_name = instance['transaction__account__first_name']
        except Exception as e:
            first_name = ''
        try:
            last_name = instance['transaction__account__last_name']
        except Exception as e:
            last_name = ''
        full_name = f'{first_name.title()} {last_name.title()}'
        if full_name != ' ' and full_name != '' and full_name:
            return full_name
        else:
            try:
                card = Card.objects.get(account_id=instance['transaction__account_id'])
                return card.number
            except Card.DoesNotExist:
                return ''
            except Exception as e:
                print(e)
                return ''

    def get_email(self, instance):
        try:
            return instance['transaction__account__email']
        except Exception as e:
            return ''

    def get_image(self, instance):
        try:
            return instance['transaction__account__image']
        except Exception as e:
            return ''

    def get_total_carbon_saving(self, instance):
        try:
            return instance['total_carbon_saving']
        except Exception as e:
            return 0

    def get_rank(self, instance):
        try:
            return instance['rank']
        except Exception as e:
            return 0
