import json
import re
from abc import ABC

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound
from config.models import Config
from inbox.caches import cache_account_count
from log.models import Log
from utils.datetime import convert_to_local
from utils.encryption import AESCipher
from utils.rest_framework.serializers import Base64ImageField
from .models import Account, Session, Forgot, KYCAccount, IdentityVerification


def check_email(value):
    if re.compile('[^@]+@[^@]+\.[^@]+').search(value):
        return True
    else:
        return False


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)


# TODO: Move to utils
def check_password(value):
    if re.compile('(?=.{8,})(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*()_+|~=`{}:;<>?,.])').match(value):
        return True
    else:
        return False


class AccountAllSerializer(serializers.ModelSerializer):
    id_card = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Account
        exclude = ['password',
                   'user_permissions',
                   'extra',
                   'image',
                   'uuid',
                   'is_force_reset_password',
                   'datetime_update'
                   ]

    def get_id_card(self, account):
        return account.id_card_decrypt

    def get_gender(self, account):
        return account.get_gender_display()

    def get_is_active(self, account):
        return 'Active' if account.is_active else 'Inactive'


class AccountListMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            'first_name',
            'last_name',
            'image',
        )


class AccountPartnerSerializer(serializers.ModelSerializer):
    mcard = serializers.SerializerMethodField()
    is_verified_phone = serializers.SerializerMethodField()
    account_register_type = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            'id',
            'first_name',
            'last_name',
            'mcard',
            'email',
            'phone',
            'is_verified_email',
            'is_verified_phone',
            'account_register_type'
        ]

    def get_mcard(self, account):
        from card.models import Card
        try:
            card = Card.objects.get(type='m_card', account=account)
            return card.number
        except Card.DoesNotExist:
            return ''
        except Exception as e:
            return ''

    def get_is_verified_phone(self, account):
        return False

    def get_account_register_type(self, account):
        from card.models import Card
        try:
            card = Card.objects.get(type='m_card', account=account)
            return 'm_card'
        except Card.DoesNotExist:
            return 'unknow'
        except Exception as e:
            return 'unknow'


class AccountListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            'title',
            'first_name',
            'last_name',
            'email',
            'username',
            'image',
        )


class AccountVerifyEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'kyc_status',
            'is_verified_email',
            'is_force_reset_password',
            'is_accepted_kyc_consent',
            'is_accepted_active_consent'
        )


class AccountSerializer(serializers.ModelSerializer):
    image = Base64ImageField(allow_empty_file=True, allow_null=True, required=False)
    id_card = serializers.SerializerMethodField()
    notification_count = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    # kyc_profile = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
            'title',
            'first_name',
            'first_name_thai',
            'last_name',
            'last_name_thai',
            'email',
            'username',
            'phone',
            'image',
            'code',
            'sol_public_key',
            'bsc_public_key',
            'id_card',
            'is_accepted_active_consent',
            'is_accepted_kyc_consent',
            # 'kyc_status',
            'is_superuser',
            'is_admin',
            'is_verified_email',
            'notification_count',
            'currency',
            'carbon_saving',
            # 'kyc_profile'
        )
        read_only_fields = ('force_token',
                            'is_accepted_active_consent',
                            'sol_public_key',
                            'bsc_public_key',
                            'is_superuser',
                            'is_admin',
                            'currency',
                            'carbon_saving'
                            )

    def get_is_verified_email(self, account):
        if Config.pull_value('config-verify-email-is-enabled'):
            return account.is_verified_email
        return True
    def get_id_card(self, account):
        return account.id_card_decrypt

    def get_currency(self, account):
        currency_dict = Config.pull_value('config-cero-coin-per-bath')
        return currency_dict if currency_dict else {"CERO": 1, "THB": 1}

    def get_notification_count(self, account):
        count = cache_account_count(account)
        return count.count

    def get_kyc_profile(self, account):
        kyc_account = KYCAccount.objects.filter(account_id=account.id).first()
        return KYCAccountSerializer(kyc_account).data if kyc_account else ''


class UserAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            'id',
            'username',
            'email'
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    title = serializers.IntegerField(default=0)
    image = Base64ImageField(allow_empty_file=True, allow_null=True, required=False)
    extra = serializers.DictField(default={}, required=False, allow_null=True)

    class Meta:
        model = Account
        fields = (
            'title',
            'first_name',
            'first_name_thai',
            'middle_name',
            'middle_name_thai',
            'last_name',
            'last_name_thai',
            'gender',
            'phone',
            'address',
            'image',
            'date_birth',
            'count_age',
            'code',
            'id_card',
            'laser_code',
            'is_active',
            'is_accepted_kyc_consent',
            'extra',
        )

    # def update(self, account, validated_data):
    #     #TODO : remove this 'if' after clear all conflict in delete account fields models
    #     id_card = AESCipher(settings.SECRET_KEY).encrypt(validated_data.get('id_card', '').strip())
    #     account_kyc = KYCAccount.objects.filter(account_id=account.id).first()
    #     if 'is_accepted_kyc_consent' in validated_data and validated_data['is_accepted_kyc_consent']:
    #         #TODO : mark for OTP
    #         if account_kyc:
    #             account_kyc.title = account.title if account.title else 0
    #             account_kyc.first_name = account.first_name if account.first_name else ''
    #             account_kyc.first_name_thai = account.first_name_thai if account.first_name_thai else ''
    #             account_kyc.middle_name = account.middle_name if account.middle_name else ''
    #             account_kyc.middle_name_thai = account.middle_name_thai if account.middle_name_thai else ''
    #             account_kyc.last_name = account.last_name if account.last_name else ''
    #             account_kyc.last_name_thai = account.last_name_thai if account.last_name_thai else ''
    #             account_kyc.id_card = id_card if id_card else None
    #             account_kyc.laser_code = account.laser_code if account.laser_code else None
    #             account_kyc.is_accepted_kyc_consent = account.is_accepted_kyc_consent if account.is_accepted_kyc_consent else False
    #             account_kyc.kyc_status = 2
    #             account_kyc.phone = account.phone if account.phone else ''
    #             account_kyc.date_birth = account.date_birth if account.date_birth else None
    #             account_kyc.save()
    #         else:
    #             account_kyc = KYCAccount.objects.create(
    #                 account_id=account.id,
    #                 title=account.title,
    #                 first_name=account.first_name,
    #                 first_name_thai=account.first_name_thai,
    #                 middle_name=account.middle_name,
    #                 middle_name_thai=account.middle_name_thai,
    #                 last_name=account.last_name,
    #                 last_name_thai=account.last_name_thai,
    #                 id_card=id_card,
    #                 laser_code=account.laser_code,
    #                 id_front_image=account.id_front_image,
    #                 id_back_image=account.id_back_image,
    #                 id_selfie_image=account.id_selfie_image,
    #                 is_accepted_kyc_consent=account.is_accepted_kyc_consent,
    #                 kyc_status=account.kyc_status,
    #                 phone=account.phone,
    #                 date_birth=account.date_birth
    #             )
    #
    #     if 'image' in validated_data:
    #         # upload new avatar
    #         if validated_data['image']:
    #             validated_data['image_log'] = validated_data['image']
    #
    #     for field in self.fields:
    #         if field in validated_data:
    #             setattr(account, field, validated_data.get(field))
    #
    #     if (validated_data.get('is_force_reset_password') is True) or (validated_data.get('is_active') is False):
    #         Session.remove(account.id)
    #
    #     if validated_data.get('is_active'):
    #         account.last_active = timezone.now()
    #
    #     if validated_data.get('id_card'):
    #         account.id_card = id_card
    #
    #     account.save()
    #     return super().update(account_kyc, validated_data)


class UserUpdatePhotoKYCSerializer(serializers.ModelSerializer):
    id_front_image = Base64ImageField(allow_empty_file=True, allow_null=True, required=False)
    id_back_image = Base64ImageField(allow_empty_file=True, allow_null=True, required=False)
    id_selfie_image = Base64ImageField(allow_empty_file=True, allow_null=True, required=False)

    class Meta:
        model = KYCAccount
        fields = (
            'id',
            'id_front_image',
            'id_back_image',
            'id_selfie_image',
        )

    def update(self, account, validated_data):
        check_point = True
        if 'id_front_image' in validated_data:
            if validated_data['id_front_image']:
                validated_data['id_front_image_log'] = validated_data['id_front_image']
            else:
                check_point = False


        if 'id_back_image' in validated_data:
            if validated_data['id_back_image']:
                validated_data['id_back_image_log'] = validated_data['id_back_image']
            else:
                check_point = False

        if 'id_selfie_image' in validated_data:
            if validated_data['id_selfie_image']:
                validated_data['id_selfie_image_log'] = validated_data['id_selfie_image']
            else:
                check_point = False
        if check_point:
            account.kyc_status = 2
        account.save()
        return super().update(account, validated_data)


class MiniAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'language',
            'code',
            'sol_public_key',
            'bsc_public_key',
        )


class KYCAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCAccount
        fields = "__all__"


class ProfileUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(allow_empty_file=True, allow_null=True, required=False)

    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'image', 'phone', 'language')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(min_length=settings.PASSWORD_MIN)
    is_remember = serializers.BooleanField(default=True)
    # language = serializers.CharField(max_length=24, allow_blank=True, required=False, default='en')
    is_vekin_login = serializers.BooleanField(allow_null=True, required=False)

    def validate_username(self, value):
        key_login = Config.pull_value('account-login-key')
        if 'email' in key_login and 'or' not in key_login:
            if not check_email(value):
                raise ValidationError('Not Email Format')
        return value


class LoginCardSerializer(serializers.Serializer):
    number = serializers.CharField()
    type = serializers.CharField()
    password = serializers.CharField()


class ValidateSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    token = serializers.CharField(required=False)


class OauthValidateSerializer(serializers.Serializer):
    code = serializers.CharField()
    is_web = serializers.BooleanField(default=True)


class SSORedirectSerializer(serializers.Serializer):
    return_path = serializers.CharField(max_length=255, required=False)


class RegisterSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    is_accepted_active_consent = serializers.BooleanField(default=False)
    is_get_news = serializers.BooleanField(default=False)
    is_share_data = serializers.BooleanField(default=False)


class LoginSocialSerializer(serializers.Serializer):
    social_type = serializers.CharField(max_length=255)
    token = serializers.CharField(max_length=9999)


class LoginSSOSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(min_length=settings.PASSWORD_MIN)
    site = serializers.CharField(default='SSO')
    profile_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)


class AccountBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            'id',
            'email'
        )


class DeleteAccountSerializer(serializers.Serializer):
    pass

class ConfirmDeleteSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
