# Generated by Django 5.0.2 on 2025-03-13 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0012_alter_scraperrun_main_run'),
    ]

    operations = [
        migrations.AddField(
            model_name='mainrun',
            name='execution_time',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='scraperrun',
            name='execution_time',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
