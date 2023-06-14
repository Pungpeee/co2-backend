from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from config.models import Config
from mailer.tasks import send_mail
from utils.datetime import convert_to_local


class Transaction(models.Model):
    COIN_CHOICES = (
        (-1, "no_data"),
        (1, "CERO"),
        (2, "GREEN"),
        (3, "THB")
    )

    METHOD_CHOICES = (
        (-1, "waiting"),
        (1, "sent"),
        (2, "receive"),
        (3, "top_up"),
        (4, "activity"),
        (5, "withdraw"),
        (6, "swap")
    )

    STATUS_CHOICES = (
        (-5, "refund"),
        (-4, "waiting_for_refund"),
        (-3, "cancel"),
        (-2, "reject"),
        (-1, "pending"),
        (1, "waiting_for_payment"),
        (2, "success")
    )

    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    desc = models.TextField(blank=True)
    transaction_hash = models.CharField(max_length=200, blank=True, null=True, default=None)
    source_key = models.CharField(max_length=200, blank=True, null=True, default=None)
    destination_key = models.CharField(max_length=200, blank=True, null=True, default=None)

    values = models.FloatField(default=0.0)
    thb_values = models.FloatField(default=0.0)
    paid_by = models.CharField(max_length=200, blank=True, null=True, default=None)

    coin = models.IntegerField(choices=COIN_CHOICES, db_index=True, default=-1)
    method = models.IntegerField(choices=METHOD_CHOICES, db_index=True, default=-1)
    status = models.IntegerField(choices=STATUS_CHOICES, db_index=True, default=-1)
    rate_per_usdt = models.FloatField(db_index=True, default=0.00)

    datetime_start = models.DateTimeField(null=True, blank=True)
    datetime_end = models.DateTimeField(null=True, blank=True)

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True)

    datetime_cancel = models.DateTimeField(null=True, blank=True)
    datetime_complete = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-datetime_create']

    def __str__(self):
        return str(self.id)

    @property
    def is_reject(self):
        from django.utils import timezone
        if self.status == -2:
            return True
        elif self.datetime_end is not None:
            return timezone.now() > self.datetime_end
        else:
            return False

    @property
    def datetime_create_str(self):
        datetime_create = convert_to_local(self.datetime_create)
        return datetime_create.strftime("%c") if datetime_create else '-'

    @property
    def day_left(self):
        from django.utils import timezone

        if self.datetime_start is None:
            return -1  # TODO : Limit system
        elif self.datetime_end is None:
            return -1
        else:
            return (self.datetime_end - timezone.now()).days + 1

    @property
    def is_active(self):
        return self.status == 0

    @property
    def status_label(self):
        return self.get_status_display().replace("_", " ").title()

    @staticmethod
    def pull(id):
        transaction = Transaction.objects.get(id=id)
        return transaction if transaction else None

    @staticmethod
    def send_topup_noti(transaction_id, topup_status):
        prefix = Config.pull_value('mailer-subject-prefix')
        header_image = Config.pull_value('mailer-header-image')
        icon_image = Config.pull_value('mailer-icon-image')

        transaction = Transaction.objects.filter(id=transaction_id).first()
        if not transaction:
            return None

        email = transaction.account.email

        if topup_status == -2: # Reject
            subject = '%s - Your top-up has rejected' % prefix
            body = render_to_string(
                'mailer/transaction/TopupReject.html',
                {
                    'header_image': settings.CO2_API_URL + header_image,
                    'mail_icon': settings.CO2_API_URL + icon_image,
                    'thb_amount': transaction.thb_values
                }
            )
            send_mail(email, subject, body, 1)

        elif topup_status == -1: # waiting for approve
            subject = '%s - Payment verification is in process' % prefix
            body = render_to_string(
                'mailer/transaction/PaymentInProcess.html',
                {
                    'header_image': settings.CO2_API_URL + header_image,
                    'mail_icon': settings.CO2_API_URL + icon_image,
                }
            )
            send_mail(email, subject, body, 1)
        elif topup_status == 2: # Approve
            subject = '%s - Your top-up has approved' % prefix
            coin_dict = dict(Transaction.COIN_CHOICES)
            body = render_to_string(
                'mailer/transaction/TopupSuccess.html',
                {
                    'header_image': settings.CO2_API_URL + header_image,
                    'mail_icon': settings.CO2_API_URL + icon_image,
                    'thb_amount': transaction.thb_values,
                    'coin_amount': transaction.values,
                    'coin_name': coin_dict[int(transaction.coin)] if transaction and transaction.coin else '-'
                }
            )
            send_mail(email, subject, body, 1)

    def set_cancel(self):
        self.datetime_end = datetime.now()
        self.datetime_cancel = datetime.now()
        self.status = -3
        self.save(update_fields=['datetime_end', 'status', 'datetime_cancel', 'datetime_update'])

@receiver(post_save, sender=Transaction)
def update_carbon_saving(sender, instance, created, **kwargs):
    from activity.models import CarbonActivity
    from account.models import Account
    if instance and instance.method == 4 and instance.status == 2:
        carbon = CarbonActivity.objects.filter(
            transaction__method=4,
            transaction__status=2,
            transaction__account_id=instance.account_id
        ).aggregate(
            total_carbon_saving=Sum('carbon_saving')
        )
        account = Account.objects.filter(id=instance.account_id).first()
        account.carbon_saving = carbon['total_carbon_saving']
        account.save()


class Payment(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    code = models.CharField(max_length=200, blank=True, null=True, default=None)
    qrcode = models.ImageField(upload_to='transaction/qrcode/%Y/%m/', null=True, blank=True)
    payment_slip = models.ImageField(upload_to='account/payment_slip/%Y/%m/', null=True, blank=True)

    ref_code_1 = models.CharField(max_length=200, blank=True, null=True, default=None)
    ref_code_2 = models.CharField(max_length=200, blank=True, null=True, default=None)

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True)

    datetime_stamp = models.DateTimeField(auto_now_add=True, db_index=True, null=True, blank=True)

    class Meta:
        ordering = ['-datetime_create']

    def __str__(self):
        return str(self.id)

    @property
    def datetime_stamp_str(self):
        datetime_stamp = convert_to_local(self.datetime_stamp)
        return datetime_stamp.strftime("%c") if datetime_stamp else '-'

