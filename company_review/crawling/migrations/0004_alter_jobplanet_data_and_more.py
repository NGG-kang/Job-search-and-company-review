# Generated by Django 4.0.1 on 2022-01-29 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawling', '0003_kreditjob_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobplanet',
            name='data',
            field=models.JSONField(blank=True),
        ),
        migrations.AlterField(
            model_name='kreditjob',
            name='company_base_content',
            field=models.JSONField(blank=True),
        ),
        migrations.AlterField(
            model_name='kreditjob',
            name='company_info_data',
            field=models.JSONField(blank=True),
        ),
        migrations.AlterField(
            model_name='kreditjob',
            name='company_jobdam',
            field=models.JSONField(blank=True),
        ),
    ]
