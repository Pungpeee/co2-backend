from django.conf import settings
from django.db import models


class AccountLog(models.Model):
    GENDER_CHOICES = (
        (0, 'Not set'),
        (1, 'Male'),
        (2, 'Female'),
        (3, 'Other'),
    )

    STATUS_CHOICE = (
        (-2, 'inactive'),
        (-1, 'suspect'),
        (1, 'active'),
        (2, 'Delete')
    )

    account_id = models.IntegerField(db_index=True, default=-1)
    gender = models.IntegerField(choices=GENDER_CHOICES, default=-1)
    age = models.IntegerField(db_index=True, default=-1)
    status = models.IntegerField(choices=STATUS_CHOICE, default=0)

    class Meta:
        ordering = ['-id']