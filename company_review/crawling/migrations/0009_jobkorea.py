# Generated by Django 4.0.1 on 2022-02-11 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawling', '0008_alter_jobplanet_search_address_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobKorea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(default='', max_length=100)),
                ('company_pk', models.CharField(max_length=100, unique=True)),
                ('data', models.JSONField(blank=True, default=dict)),
                ('search_address', models.CharField(blank=True, default='', max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
