import datetime
import random
import string

import six
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import status

from account_log.models import AccountLog
from config.models import Config
from log.models import Log
from mailer.tasks import send_mail
from utils.datetime import convert_to_local
from utils.generator import generate_OTP
from utils.parse import parse
from utils.phone_number import reformat_phone_number

def generate_username():
    import random
    import string
    return ''.join(random.sample(string.ascii_lowercase, 6))


class AccountManager(BaseUserManager):

    def create_user(self, username, password):
        if username is None:
            raise ValueError('The given username must be set')

        user = self.model(
            username=username
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, is_accepted_active_consent=True):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """

        user = self.create_user(username, password)
        user.is_admin = True
        user.is_superuser = True
        user.type = 1
        user.is_accepted_active_consent = is_accepted_active_consent
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser, PermissionsMixin):
    TYPE = (
        (0, 'user'),
        (1, 'system_user'),
    )

    KYC_STATUS = (
        (-2, 'reject'),
        (-1, 'no_process'),
        (1, 'not_verify'),
        (2, 'in_review'),
        (3, 'approve')
    )

    TITLE_CHOICES = (
        (0, 'Not set'),
        (1, 'Mr.'),
        (2, 'Mrs.'),
        (3, 'Ms.'),
    )

    GENDER_CHOICES = (
        (0, 'Not set'),
        (1, 'Male'),
        (2, 'Female'),
        (3, 'Other'),
    )

    external_id = models.CharField(max_length=32, blank=True, null=True, default=None)
    # ref_code = models.CharField(max_length=32, db_index=True, blank=True, null=True, default=None) Auto gen ref code
    code = models.CharField(max_length=32, db_index=True, blank=True, null=True, default=None)
    sol_public_key = models.CharField(max_length=128, db_index=True, blank=True, null=True, default=None)
    bsc_public_key = models.CharField(max_length=128, db_index=True, blank=True, null=True, default=None)

    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
        blank=True,
        null=True,
    )

    email = models.EmailField(
        verbose_name='Email address',
        max_length=255,
        db_index=True,
        blank=True,
        null=True,
    )

    title = models.IntegerField(choices=TITLE_CHOICES, default=0)

    first_name = models.CharField(max_length=120, db_index=True, blank=True)
    first_name_thai = models.CharField(max_length=120, db_index=True, blank=True) #TODO remove @Jade

    middle_name = models.CharField(max_length=120, db_index=True, blank=True)
    middle_name_thai = models.CharField(max_length=120, db_index=True, blank=True) #TODO remove @Jade

    last_name = models.CharField(max_length=120, db_index=True, blank=True)
    last_name_thai = models.CharField(max_length=120, db_index=True, blank=True) #TODO remove @Jade

    id_card = models.CharField(max_length=255, blank=True, null=True)  # Encrypt #TODO remove @Jade
    laser_code = models.CharField(max_length=255, blank=True, null=True)  # TODO remove @Jade
    id_front_image = models.ImageField(upload_to='account/KYC/%Y/%m/', null=True, blank=True) #TODO remove @Jade
    id_back_image = models.ImageField(upload_to='account/KYC/%Y/%m/', null=True, blank=True) #TODO remove @Jade
    id_selfie_image = models.ImageField(upload_to='account/KYC/%Y/%m/', null=True, blank=True) #TODO remove @Jade
    is_accepted_kyc_consent = models.BooleanField(default=False)  # TODO remove @Jade
    kyc_status = models.IntegerField(choices=KYC_STATUS, default=-1)  # TODO Change to check from relate object @Jade

    image = models.ImageField(upload_to='account/%Y/%m/', null=True, blank=True)  # MH
    type = models.IntegerField(choices=TYPE, default=0)  # MH
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0)
    language = models.CharField(max_length=12, blank=True, default='en')  # MH

    is_admin = models.BooleanField(default=False)  # MH
    is_operator = models.BooleanField(default=False)
    is_force_reset_password = models.BooleanField(default=False)

    phone = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    address = models.TextField(blank=True)

    is_verified_email = models.BooleanField(default=False)  # MH

    is_get_news = models.BooleanField(default=True)
    is_share_data = models.BooleanField(default=True)

    count_age = models.FloatField(default=-1)
    date_birth = models.DateField(null=True, blank=True) #TODO Made relate with KYC and can't update @Jade

    extra = models.TextField(default='{}')  # JSON

    is_active = models.BooleanField(default=True, db_index=True)
    is_accepted_active_consent = models.BooleanField(default=False, db_index=True)  # MH
    datetime_update = models.DateTimeField(auto_now=True, null=True)  # MH
    objects = AccountManager()

    # cache field
    carbon_saving = models.FloatField(default=0.0)

    USERNAME_FIELD = 'username'

    class Meta:
        ordering = ['-id']

    @property
    def title_name_display(self):
        return self.get_title_display()

    @property
    def date_birth_str(self):
        return self.date_birth.strftime("%d-%B-%Y")

    @property
    def get_device_profile_list(self):
        return self.device_profile_set

    @property
    def is_dashboard_permission(self):
        return self.groups.filter(permissions__codename='view_dashboard').exists()

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def kyc_status_display(self):
        return self.get_kyc_status_display().replace("_", " ").title()

    @property
    def status(self):
        return 1 if self.is_active else -2

    @property
    def check_password_expire(self):
        from config.models import Config
        from datetime import timedelta

        if Config.pull_value('config-account-password-expire'):
            forgot = Forgot.objects.filter(account_id=self.id, status=2).order_by('-datetime_create').first()
            if forgot is None:
                password_create = self.date_joined
            else:
                password_create = forgot.datetime_create
            days = Config.pull_value('config-account-age-password')
            if days > 0 and timedelta(days=days) + password_create < timezone.now():
                return True
        return False

    @property
    def id_card_decrypt(self):
        from utils.encryption import AESCipher
        if self.id_card:
            if len(self.id_card) > 13:
                try:
                    return AESCipher(settings.SIGN_KEY).decrypt(self.id_card)
                except:
                    return ''
            else:
                return self.id_card
        return ''

    @property
    def id_card_encrypt(self):
        from utils.encryption import AESCipher
        if self.id_card:
            if len(self.id_card) > 13:
                try:
                    return AESCipher(settings.SIGN_KEY).encrypt(self.id_card)
                except:
                    return ''
            else:
                return self.id_card
        return ''

    def get_full_name(self):
        import re
        return re.sub(' +', ' ', '{0} {1}'.format(self.first_name, self.last_name))

    def get_full_name_thai(self):
        import re
        return re.sub(' +', ' ', '{0} {1}'.format(self.first_name_thai, self.last_name_thai))

    @staticmethod
    def pull(id):
        from .caches import cache_account
        return cache_account(id)

    @staticmethod
    def create_verify_email(email, token, site_url):
        prefix = Config.pull_value('mailer-subject-prefix')
        header_image = Config.pull_value('mailer-header-image')
        icon_image = Config.pull_value('mailer-icon-image')
        subject = '%s - Verify Email' % prefix
        link = site_url + 'account/verify-email/?token=%s' % (token)

        body = render_to_string('mailer/account/verify_email.html',
                                {
                                    'link': link,
                                    'header_image': settings.CO2_API_URL + header_image,
                                    'mail_icon': settings.CO2_API_URL + icon_image
                                }
                                )
        send_mail(email, subject, body, 1)

    @staticmethod
    def send_login_noti(email, ip):
        prefix = Config.pull_value('mailer-subject-prefix')
        header_image = Config.pull_value('mailer-header-image')
        icon_image = Config.pull_value('mailer-icon-image')
        subject = '%s - Your account has been logged in' % prefix
        dt_n_str = convert_to_local(timezone.now()).strftime('%Y-%m-%d %H:%M:%S')
        # 2022-02-22 18:22:22 (UTC) for example

        body = render_to_string(
            'mailer/account/LoginNotification.html',
            {
                'header_image': settings.CO2_API_URL + header_image,
                'mail_icon': settings.CO2_API_URL + icon_image,
                'ip': ip,
                'dt_n_str' : dt_n_str,
                'time_zone' : settings.TIME_ZONE
            }
        )
        send_mail(email, subject, body, 1)

    @staticmethod
    def send_change_password_noti(email):
        prefix = Config.pull_value('mailer-subject-prefix')
        header_image = Config.pull_value('mailer-header-image')
        icon_image = Config.pull_value('mailer-icon-image')
        subject = '%s - Your password has changed' % prefix

        body = render_to_string(
            'mailer/account/PasswordChanged.html',
            {
                'header_image': settings.CO2_API_URL + header_image,
                'mail_icon': settings.CO2_API_URL + icon_image,
            }
        )
        send_mail(email, subject, body, 1)

    @staticmethod
    def send_email_kyc(email, status):
        prefix = Config.pull_value('mailer-subject-prefix')
        header_image = Config.pull_value('mailer-header-image')
        icon_image = Config.pull_value('mailer-icon-image')
        # Pending
        if status == 2 :
            subject = '%s - KYC Pending' % prefix

            body = render_to_string(
                'mailer/account/KYCPending.html',
                {
                    'header_image': settings.CO2_API_URL + header_image,
                    'mail_icon': settings.CO2_API_URL + icon_image
                }
            )
            send_mail(email, subject, body, 1)
        # Reject
        elif status == -2:
            subject = '%s - KYC Rejected' % prefix

            body = render_to_string(
                'mailer/account/KYCReJect.html',
                {
                    'header_image': settings.CO2_API_URL + header_image,
                    'mail_icon': settings.CO2_API_URL + icon_image
                }
            )
            send_mail(email, subject, body, 1)

        elif status == 3:
            subject = '%s - KYC Approve' % prefix

            body = render_to_string(
                'mailer/account/KYCApprove.html',
                {
                    'header_image': settings.CO2_API_URL + header_image,
                    'mail_icon': settings.CO2_API_URL + icon_image
                }
            )
            send_mail(email, subject, body, 1)

    @staticmethod
    def pull_account(username_or_email):
        _account = Account.objects.filter(username=username_or_email, is_active=True).first()
        if _account is None:
            _account = Account.objects.filter(email=username_or_email, is_active=True).exclude(
                email__isnull=True).first()
        return _account

    def __str__(self):
        return str(self.email)

    def forgot_password(self):
        from utils.generator import generate_token

        while True:
            token = generate_token(32)
            if not Forgot.objects.filter(token=token, method=1, status=1).exists():
                break

        Forgot.objects.create(
            account=self,
            token=token,
            method=1,
            status=1
        )
        return token

    def delete_request(self):
        from utils.generator import generate_token

        while True:
            token = generate_token(32)
            if not RequestDelete.objects.filter(token=token).exists():
                break

        RequestDelete.objects.create(
            account=self,
            token=token
        )
        return token

    def has_perm(self, perm, group=None, obj=None):
        if self.is_superuser and group is None:
            return True

        from .caches import cached_auth_permission

        def _get_permissions(user_obj, group):
            perms = cached_auth_permission(user_obj.id, group)
            return set("%s.%s" % (ct, name) for ct, name in perms)

        # Skip is_superuser
        if group is None:
            code = '_perm_cache'
        else:
            code = '_perm_cache_%s' % group.id
        if not hasattr(self, code):
            setattr(self, code, _get_permissions(self, group))
        return perm in getattr(self, code)

@receiver(post_save, sender=Account)
def create_account_log(sender, instance, created, **kwargs):
    from script.account_transfer_data_log import calculate_age
    if instance.is_active:
        if created:
            AccountLog.objects.create(
                account_id=instance.id,
                gender=instance.gender,
                age=calculate_age(instance.date_birth) if instance.date_birth else -1,
                status=instance.status
            )
        else:
            acc_log = AccountLog.objects.filter(account_id=instance.id).last()
            if acc_log:
                status = 1
                if not instance.is_active and (instance.first_name or instance.last_name or instance.first_name_thai or instance.last_name_thai):
                    status = -2
                elif instance.is_active and not (instance.first_name or instance.last_name or instance.first_name_thai or instance.last_name_thai):
                    status = -1
                elif not instance.is_active and not (instance.first_name or instance.last_name or instance.first_name_thai or instance.last_name_thai):
                    status = 2
                acc_log.gender = instance.gender
                acc_log.age = calculate_age(instance.date_birth) if instance.date_birth else -1
                acc_log.status = status
                acc_log.save()


def generate_token_field():
    token = ''.join(random.choice(string.digits) for _ in range(6))
    if IdentityVerification.objects.filter(token=token).exists():
        generate_token_field()
    return token

def generate_ref_code_field():
    token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    if IdentityVerification.objects.filter(token=token).exists():
        generate_token_field()
    return token


class IdentityVerification(models.Model):
    STATUS_CHOICES = (
        (-1, 'deactivate'),
        (1, 'activate'),
        (2, 'verifying'),
        (3, 'expired'),
    )

    METHOD_CHOICES = (
        (0, 'not_set'),
        (1, 'email'),
        (2, 'phone_number')
    )

    SENT_METHOD_CHOICE = (
        (1, 'email'),
        (2, 'sms')
    )

    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(unique=True, default=generate_token_field, max_length=120, db_index=True, editable=False)
    ref_code = models.CharField(unique=True, default=generate_ref_code_field, max_length=120, db_index=True, editable=False)

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, db_index=True)
    method = models.IntegerField(choices=METHOD_CHOICES, default=0, db_index=True)
    send_method = models.IntegerField(choices=SENT_METHOD_CHOICE, default=1, db_index=True)

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_expire = models.DateTimeField(null=True, blank=True)

    class Meta:
        default_permissions = ()

    @property
    def is_verify(self):
        if self.datetime_expire > timezone.now() and self.status == 1:
            return True
        else:
            self.status = 3
            self.save(update_fields=['status'])
            return False

    @staticmethod
    def send_verification(account_id, method, send_method):
        account = Account.objects.get(id=account_id)
        IdentityVerification.objects.filter(account_id=account.id, status=1).update(status=-1)
        expired_time = Config.pull_value('config-verification-expired-time')
        datetime_expire = timezone.now() + datetime.timedelta(minutes=int(expired_time))
        identity = IdentityVerification.objects.create(
            account_id=account.id,
            method=method,
            send_method=send_method,
            datetime_expire=datetime_expire
        )

        if method == 1 and send_method == 1:
            from inbox.tasks_push_email_verification import task_push_email_verification
            if account.is_verified_email:
                return False
            task_push_email_verification.delay(token=identity.token)
            return

        elif method == 2 and send_method == 2:
            from alert.models import Alert
            from account.send_sms_infobip_tasks import task_sent_verification_infobip

            if not Config.pull_value('config-is-enable-infobip'):
                return {'error_message': 'Infobip service not enable'}, status.HTTP_406_NOT_ACCEPTABLE

            phone_number = reformat_phone_number(account.phone)
            if not phone_number:
                Log.push(None, 'ACCOUNT', 'ACCOUNT_LOGOUT', account,
                         'Sent Verification code fail because wrong format phone number', status.HTTP_400_BAD_REQUEST)
                return
            alert = Alert.objects.create(
                account_id=account.id,
                code='sent_otp_verification_%s' % account.id,
                status=0,
                action_type=3
            )
            task_sent_verification_infobip.delay(account.id, phone_number, identity.token, identity.ref_code, alert.id)
            return identity

    def generate_otp_code(account):
        now = timezone.now()
        expired_time = Config.pull_value('config-verification-expired-time')
        data = IdentityVerification.objects.filter(account=account, status=1,
                                              datetime_expire__gte=timezone.localtime(now)).first()
        if data is None:
            OTP_code = generate_OTP()
            datetime_expire = timezone.now() + datetime.timedelta(minutes=int(expired_time))
            data = IdentityVerification.objects.create(account=account, token=OTP_code, status=1,
                                                  datetime_expire=datetime_expire)
        return data


class Session(models.Model):
    account = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', on_delete=models.CASCADE)
    session_key = models.CharField(max_length=255, db_index=True)
    token = models.TextField(null=True, blank=True)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)

    @staticmethod
    def push(account, session_key, token=None):
        from importlib import import_module
        from django.conf import settings
        from config.models import Config
        from .caches import cache_account_delete

        is_single = Config.pull_value('account-login-single')
        if is_single:
            session = Session.objects.filter(account=account).first()
            if session is not None:
                if session.session_key != session_key:
                    session_store = import_module(settings.SESSION_ENGINE).SessionStore
                    s = session_store(session_key=session.session_key)
                    s.delete()
                    session.session_key = session_key
                    session.token = token
                    session.save()
            else:
                Session.objects.create(account=account, session_key=session_key, token=token)
        else:
            Session.objects.create(account=account, session_key=session_key, token=token)
        cache_account_delete(account.id)

    @staticmethod
    def remove(account_id, session_key=None):
        from importlib import import_module
        from django.conf import settings
        from config.models import Config
        from .caches import cache_account_delete

        is_single = Config.pull_value('account-login-single')
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        if is_single or session_key is None:
            for session in Session.objects.filter(account_id=account_id):
                _session = session_store(session.session_key)
                _session.delete()
                session.delete()
        else:
            for session in Session.objects.filter(account_id=account_id, session_key=session_key):
                _session = session_store(session.session_key)
                _session.delete()
                session.delete()
        cache_account_delete(account_id)


class KYCAccount(models.Model):
    TITLE_CHOICES = (
        (0, 'Not set'),
        (1, 'Mr.'),
        (2, 'Mrs.'),
        (3, 'Ms.'),
    )

    KYC_STATUS = (
        (-2, 'reject'),
        (-1, 'no_process'),
        (1, 'not_verify'),
        (2, 'in_review'),
        (3, 'approve')
    )

    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.IntegerField(choices=TITLE_CHOICES, default=0)
    first_name = models.CharField(max_length=120, db_index=True, blank=True)
    first_name_thai = models.CharField(max_length=120, db_index=True, blank=True)

    middle_name = models.CharField(max_length=120, db_index=True, blank=True)
    middle_name_thai = models.CharField(max_length=120, db_index=True, blank=True)

    last_name = models.CharField(max_length=120, db_index=True, blank=True)
    last_name_thai = models.CharField(max_length=120, db_index=True, blank=True)

    id_card = models.CharField(max_length=255, blank=True, null=True)  # Encrypt
    laser_code = models.CharField(max_length=255, blank=True, null=True)

    id_front_image = models.ImageField(upload_to='account/KYC/%Y/%m/', null=True, blank=True)
    id_back_image = models.ImageField(upload_to='account/KYC/%Y/%m/', null=True, blank=True)
    id_selfie_image = models.ImageField(upload_to='account/KYC/%Y/%m/', null=True, blank=True)
    is_accepted_kyc_consent = models.BooleanField(default=False)
    kyc_status = models.IntegerField(choices=KYC_STATUS, default=-1)
    phone = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    date_birth = models.DateField(null=True, blank=True)
    is_mobile_verify = models.BooleanField(default=False)

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        default_permissions = ()

    @property
    def kyc_status_display(self):
        return self.get_kyc_status_display().replace("_", " ").title()

    @property
    def title_name_display(self):
        return self.get_title_display()


class RequestDelete(models.Model):
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=120, db_index=True)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        default_permissions = ()




class Forgot(models.Model):
    STATUS_CHOICES = (
        (-1, 'Deactivate'),
        (1, 'Activate'),
        (2, 'Completed'),
        (3, 'Expired'),
    )

    METHOD_CHOICES = (
        (0, '(Not set)'),
        (1, 'Forgot password'),
        (2, 'Force reset password'),
        (3, 'Change password'),
        (4, 'Forgot password OTP'),
    )

    SENT_METHOD_CHOICE = (
        (1, 'Email'),
        (2, 'SMS')
    )

    REFERENCE_ID_FORMAT = '{id:d}'

    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=120, db_index=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, db_index=True)
    method = models.IntegerField(choices=METHOD_CHOICES, default=0, db_index=True)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    send_method = models.IntegerField(choices=SENT_METHOD_CHOICE, default=1, db_index=True)
    count_failed = models.IntegerField(default=0)
    datetime_failed_limit = models.DateTimeField(null=True, blank=True)

    class Meta:
        default_permissions = ()

    @property
    def reference_id(self):
        return self.REFERENCE_ID_FORMAT.format(id=self.id)

    @property
    def lifetime(self):
        second = Config.pull_value('config-account-forgot-password-otp-age')
        return second

    @property
    def is_token_expire(self):
        from datetime import timedelta
        from django.utils import timezone

        if self.method == 2:
            return False

        second = Config.pull_value('config-account-forgot-password-otp-age')
        day_offset = timedelta(seconds=second)
        is_expired = self.datetime_create + day_offset < timezone.now()
        if is_expired and self.status != 3:
            self.status = 3
            self.save(update_fields=['status'])
        return is_expired

    @property
    def is_failed_limit(self):
        failed_limit = Config.pull_value('config-account-forgot-password-otp-failed-limit')
        is_failed_limit = self.count_failed >= failed_limit
        return is_failed_limit

    @staticmethod
    def get_pk_by_reference(reference_id):
        parse_result = parse(Forgot.REFERENCE_ID_FORMAT, reference_id)
        if not parse_result:
            return None
        else:
            return parse_result['id']

    @staticmethod
    def update_count_failed(id):
        forgot = Forgot.objects.filter(id=id).first()
        is_failed_limit = False
        if forgot:
            failed_limit = Config.pull_value('config-account-forgot-password-otp-failed-limit')
            if forgot.count_failed < failed_limit:
                forgot.count_failed += 1
                if forgot.count_failed == failed_limit:
                    is_failed_limit = True
                    forgot.status = -1
                    forgot.datetime_failed_limit = timezone.now()
                forgot.save(update_fields=['count_failed', 'status', 'datetime_failed_limit'])
        return is_failed_limit

    def get_lifetime_text(self):
        m, s = divmod(self.lifetime, 60)
        h, m = divmod(m, 60)

        hour_str = ''
        minute_str = ''
        second_str = ''

        if h > 0:
            hour_str = '{!s} hours'.format(h)
        if m > 0:
            minute_str = '{!s} minutes'.format(m)
        if s > 0:
            second_str = '{!s} seconds'.format(s)

        return hour_str + minute_str + second_str

    def get_waiting_for_renew_countdown(self):
        from datetime import timedelta
        from django.utils import timezone

        second = Config.pull_value('config-account-forgot-password-otp-renew-delay')
        day_offset = timedelta(seconds=second)
        now = timezone.now()
        countdown = ((self.datetime_create + day_offset) - now).total_seconds()
        return countdown

    def get_banned_countdown(self):
        from datetime import timedelta
        from django.utils import timezone

        countdown = 0
        second = Config.pull_value('config-account-forgot-password-otp-banned-delay')
        day_offset = timedelta(seconds=second)
        now = timezone.now()
        if self.datetime_failed_limit:
            countdown = ((self.datetime_failed_limit + day_offset) - now).total_seconds()
        return countdown


class PasswordHistory(models.Model):
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    password = models.CharField(_('password'), max_length=128)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        default_permissions = ()

    @staticmethod
    def check_password(account, password, old_password):
        def setter(password):
            account.set_password(password)
            # Password hash upgrades shouldn't be considered password changes.
            account._password = None
            account.save(update_fields=['password'])

        return check_password(password, old_password, setter)

    @staticmethod
    def check_exists(account, new_password):
        from config.models import Config
        limit_password = Config.pull_value('config-password-history')
        if limit_password > 0:
            password_history_list = PasswordHistory.objects.filter(
                account=account
            ).order_by('-datetime_create')[:limit_password]
            for old_password in password_history_list:
                if old_password.check_password(account, new_password, old_password.password):
                    return False
        return True


class Token(models.Model):
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    token = models.CharField(max_length=100, blank=True, unique=True)
    datetime_create = models.DateField(auto_now_add=True, db_index=True)

    class Meta:
        default_permissions = ()
        ordering = ['-datetime_create']


class UtilityToken(models.Model):
    NAME_CHOICES = [
        ('nft_access_token', 'NFC Access Token')
    ]

    name = models.CharField(max_length=255, choices=NAME_CHOICES)
    token = models.TextField()
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE)

    is_active = models.BooleanField(default=True)
    datetime_expire = models.DateTimeField(blank=True, null=True)

    datetime_create = models.DateTimeField(auto_now_add=True)
    datetime_update = models.DateTimeField(auto_now=True)


class KYCStep1(models.Model):
    STATUS = (
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
        ('opened', 'opened')
    )
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    title_name = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    first_name_thai = models.CharField(max_length=100, null=True, blank=True)
    last_name_thai = models.CharField(max_length=100, null=True, blank=True)
    identification_number = models.CharField(max_length=30, null=True, blank=True)
    laser_code = models.CharField(max_length=50, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    status = models.CharField(choices=STATUS, default='opened', max_length=20)

    datetime_create = models.DateTimeField(auto_now_add=True)
    datetime_update = models.DateTimeField(auto_now=True)


class KYCStep2(models.Model):
    STATUS = (
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
        ('opened', 'opened')
    )
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    card_front = models.CharField(max_length=200, blank=True, null=True)
    card_back = models.CharField(max_length=200, blank=True, null=True)
    selfie = models.CharField(max_length=200, blank=True, null=True)

    status = models.CharField(choices=STATUS, default='opened', max_length=20)

    datetime_create = models.DateTimeField(auto_now_add=True)
    datetime_update = models.DateTimeField(auto_now=True)


class KYCStep3(models.Model):
    STATUS = (
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
        ('opened', 'opened')
    )
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    face_detect = models.CharField(max_length=200, blank=True, null=True)

    status = models.CharField(choices=STATUS, default='opened', max_length=20)

    datetime_create = models.DateTimeField(auto_now_add=True)
    datetime_update = models.DateTimeField(auto_now=True)
