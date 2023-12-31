# Generated by Django 3.2.6 on 2022-03-29 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0011_alter_payment_datetime_stamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.IntegerField(choices=[(-4, 'refund'), (-3, 'cancel'), (-2, 'reject'), (-1, 'pending'), (1, 'waiting_for_payment'), (2, 'success')], db_index=True, default=-1),
        ),
    ]
