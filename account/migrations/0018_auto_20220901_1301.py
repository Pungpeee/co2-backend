# Generated by Django 3.2.6 on 2022-09-01 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0017_kycaccount_is_mobile_verify'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='public_key',
            new_name='sol_public_key',
        ),
        migrations.AddField(
            model_name='account',
            name='bsc_public_key',
            field=models.CharField(blank=True, db_index=True, default=None, max_length=128, null=True),
        ),
    ]
