# Generated by Django 3.2.6 on 2022-07-06 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alert', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='action_type',
            field=models.IntegerField(choices=[(0, 'other'), (1, 'export'), (2, 'import'), (3, 'update'), (4, 'create')], default=0),
        ),
    ]
