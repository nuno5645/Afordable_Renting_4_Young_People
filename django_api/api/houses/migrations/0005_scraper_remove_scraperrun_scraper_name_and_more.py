# Generated by Django 5.1.6 on 2025-02-27 23:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0004_rename_houses_found_scraperrun_new_houses_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scraper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('total_processed', models.IntegerField(default=0)),
                ('total_found', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'scrapers',
            },
        ),
        migrations.RemoveField(
            model_name='scraperrun',
            name='scraper_name',
        ),
        migrations.AddField(
            model_name='scraperrun',
            name='scraper',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='runs', to='houses.scraper'),
        ),
    ]
