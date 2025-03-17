# Generated by Django 5.1.6 on 2025-03-15 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VMS', '0004_visitorpreregistration_qr_code_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='qr_code',
            field=models.ImageField(blank=True, upload_to='asset_qr_codes/'),
        ),
        migrations.AddField(
            model_name='visitor',
            name='qr_code',
            field=models.ImageField(blank=True, upload_to='qr_codes/'),
        ),
    ]
