# Generated by Django 3.2.6 on 2022-07-27 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0003_auto_20220707_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carbonactivity',
            name='type',
            field=models.IntegerField(choices=[(-2, 'cancel'), (-1, 'pending'), (1, 'dining'), (2, 'shopping'), (3, 'transportation'), (4, 'recycle'), (5, 'foresting'), (6, 'others')], db_index=True, default=-1),
        ),
    ]
