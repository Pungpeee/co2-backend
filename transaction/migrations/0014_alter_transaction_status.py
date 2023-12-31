# Generated by Django 3.2.6 on 2022-07-20 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0013_auto_20220718_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.IntegerField(choices=[(-5, 'refund'), (-4, 'waiting_for_refund'), (-3, 'cancel'), (-2, 'reject'), (-1, 'pending'), (1, 'waiting_for_payment'), (2, 'success')], db_index=True, default=-1),
        ),
    ]
