# Generated by Django 3.2.6 on 2022-07-21 04:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_alter_account_carbon_saving'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestDelete',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(db_index=True, max_length=120)),
                ('datetime_create', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': (),
            },
        ),
    ]
