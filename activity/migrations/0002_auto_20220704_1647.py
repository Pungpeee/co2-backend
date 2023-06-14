# Generated by Django 3.2.6 on 2022-07-04 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='carbonactivity',
            old_name='code',
            new_name='activity_code',
        ),
        migrations.AddField(
            model_name='carbonactivity',
            name='activity_details',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='carbonactivity',
            name='activity_name',
            field=models.CharField(blank=True, db_index=True, default=None, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='carbonactivity',
            name='type',
            field=models.IntegerField(choices=[(-2, 'cancel'), (-1, 'pending'), (1, 'food_drink'), (2, 'shopping'), (3, 'transportation'), (4, 'recycle')], db_index=True, default=-1),
        ),
    ]