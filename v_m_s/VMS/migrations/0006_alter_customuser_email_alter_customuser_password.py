# Generated by Django 5.1.6 on 2025-03-20 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VMS', '0005_asset_qr_code_visitor_qr_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
    ]
