from django.db import models

# Create your models here.
from transaction.models import Transaction

'''
    activity_name ->    class           string  class (category)                [paper,plastic]
    activity_code ->    sub_class       string  sub class refer class           pa-001
    activity_details -> sub_class_name  string  sub class name refer sub class  กล่องข้าวกระดาษ สีน้ำตาล
'''


class CarbonActivity(models.Model):
    COIN_CHOICES = Transaction.COIN_CHOICES
    TYPE_CHOICE = (
        (-2, "cancel"),
        (-1, "pending"),
        (1, "dining"),
        (2, "shopping"),
        (3, "transportation"),
        (4, "recycle"),
        (5, "foresting"),
        (6, "others")
    )

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    type = models.IntegerField(choices=TYPE_CHOICE, db_index=True, default=-1)

    # Trash type from recycle activity  [TODO : remove in next phase]
    activity_code = models.CharField(max_length=32, db_index=True, blank=True, null=True, default=None)
    activity_name = models.CharField(max_length=32, db_index=True, blank=True, null=True, default=None)
    activity_details = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    #####

    coin = models.IntegerField(choices=COIN_CHOICES, db_index=True, default=-1)
    values = models.FloatField(default=0.0)  # Coin value Ex: Cero 1.10012 coin

    desc = models.TextField(blank=True, null=True)

    # kilogram
    carbon_saving = models.FloatField(default=0.0)

    # value of CERO
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-datetime_create']

    def __str__(self):
        return str(self.id)

    @property
    def account(self):
        return self.transaction.account if self.transaction else None

    @staticmethod
    def pull(id):
        carbon_activity = CarbonActivity.objects.get(id=id)
        return carbon_activity if carbon_activity else None

    def get_account(self):
        return self.transaction.account.email


