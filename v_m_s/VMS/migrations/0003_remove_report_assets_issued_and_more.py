# Generated by Django 5.1.6 on 2025-02-28 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VMS', '0002_visitor_pre_registration_visitor_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='assets_issued',
        ),
        migrations.RemoveField(
            model_name='report',
            name='assets_returned',
        ),
        migrations.RemoveField(
            model_name='report',
            name='checked_in',
        ),
        migrations.RemoveField(
            model_name='report',
            name='checked_out',
        ),
        migrations.RemoveField(
            model_name='report',
            name='visitors',
        ),
    ]
