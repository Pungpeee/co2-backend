# Generated by Django 3.2.6 on 2022-04-22 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification_template', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trigger',
            name='code',
            field=models.CharField(db_index=True, max_length=255),
        ),
    ]
