# Generated by Django 3.2.6 on 2022-02-14 06:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inbox', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=120)),
                ('body', models.TextField()),
                ('datetime_create', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('datetime_update', models.DateTimeField(auto_now=True)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Mailer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('to', models.CharField(blank=True, max_length=255, null=True)),
                ('subject', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('status', models.IntegerField(choices=[(0, 'FAILED'), (1, 'WAITING'), (2, 'SUCCESS')], default=1)),
                ('type', models.IntegerField(choices=[(1, 'Reset Password'), (2, 'Inbox'), (4, 'Notify'), (5, 'Contact')], default=0)),
                ('attach_file', models.FileField(null=True, upload_to='attach_file/%Y/%m/')),
                ('payload', models.TextField(blank=True, default='', null=True)),
                ('traceback', models.TextField(blank=True, default='', null=True)),
                ('datetime_send', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('datetime_create', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('datetime_update', models.DateTimeField(auto_now=True)),
                ('inbox', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='inbox.inbox')),
            ],
            options={
                'ordering': ['-datetime_create'],
                'default_permissions': (),
            },
        ),
    ]
