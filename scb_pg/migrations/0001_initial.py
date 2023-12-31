# Generated by Django 3.2.6 on 2022-06-02 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentConfirmation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('res_code', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('res_desc', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('transaction_id', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('confirm_id', models.CharField(blank=True, default=None, max_length=200, null=True)),
            ],
            options={
                'ordering': ['-transaction_id'],
            },
        ),
        migrations.CreateModel(
            name='SCBPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('amount', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('transaction_datetime', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('currency_code', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('transaction_type', models.CharField(choices=[('QR30', 'QR30')], max_length=255)),
                ('payee_proxy_type', models.CharField(choices=[('QR30', 'QR30')], max_length=255)),
                ('payee_proxy_id', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('payee_account_number', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('payee_name', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('payer_proxy_id', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('payer_proxy_type', models.CharField(choices=[('QR30', 'QR30')], max_length=255)),
                ('payer_name', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('payer_account_name', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('payer_account_number', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('bill_payment_ref1', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('bill_payment_ref2', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('bill_payment_ref3', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('sending_bank_code', models.CharField(blank=True, default=None, max_length=10, null=True)),
                ('receiving_bank_code', models.CharField(blank=True, default=None, max_length=10, null=True)),
                ('channel_code', models.CharField(choices=[('QR30', 'QR30')], max_length=255)),
            ],
            options={
                'ordering': ['-transaction_datetime'],
            },
        ),
    ]
