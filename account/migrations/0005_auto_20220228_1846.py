# Generated by Django 3.2.6 on 2022-02-28 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20220228_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='id_back_image',
            field=models.ImageField(blank=True, null=True, upload_to='account/KYC/%Y/%m/'),
        ),
        migrations.AddField(
            model_name='account',
            name='id_front_image',
            field=models.ImageField(blank=True, null=True, upload_to='account/KYC/%Y/%m/'),
        ),
        migrations.AddField(
            model_name='account',
            name='is_accepted_kyc_consent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='account',
            name='laser_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='gender',
            field=models.IntegerField(choices=[(0, 'Not set'), (1, 'Mr.'), (2, 'Ms.'), (3, 'Mrs.')], default=0),
        ),
        migrations.AlterField(
            model_name='identityverification',
            name='status',
            field=models.IntegerField(choices=[(-1, 'deactivate'), (1, 'activate'), (2, 'verifying'), (3, 'expired')], db_index=True, default=1),
        ),
    ]
