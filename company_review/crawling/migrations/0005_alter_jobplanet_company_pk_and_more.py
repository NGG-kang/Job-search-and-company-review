# Generated by Django 4.0.1 on 2022-01-29 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawling', '0004_alter_jobplanet_data_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobplanet',
            name='company_pk',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='kreditjob',
            name='company_pk',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
