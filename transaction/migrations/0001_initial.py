# Generated by Django 3.2.6 on 2022-03-08 11:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_hash', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('source_key', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('destination_key', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('values', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('coin', models.IntegerField(choices=[(-1, 'no_data'), (1, 'CERO'), (2, 'GREEN'), (3, 'THB')], db_index=True, default=-1)),
                ('method', models.IntegerField(choices=[(-1, 'waiting'), (1, 'sent'), (2, 'receive'), (3, 'top_up'), (4, 'activity')], db_index=True, default=-1)),
                ('status', models.IntegerField(choices=[(-2, 'reject'), (-1, 'pending'), (1, 'waiting_for_payment'), (2, 'success')], db_index=True, default=-1)),
                ('datetime_start', models.DateTimeField(blank=True, null=True)),
                ('datetime_end', models.DateTimeField(blank=True, null=True)),
                ('datetime_create', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('datetime_update', models.DateTimeField(auto_now=True)),
                ('datetime_cancel', models.DateTimeField(blank=True, null=True)),
                ('datetime_complete', models.DateTimeField(blank=True, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-datetime_create'],
            },
        ),
    ]
