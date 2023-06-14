# Generated by Django 3.2.6 on 2022-04-20 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inbox', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inbox',
            name='type',
            field=models.IntegerField(choices=[(1, 'Direct Message'), (2, 'News Update')], default=1),
        ),
    ]
