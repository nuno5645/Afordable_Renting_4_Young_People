# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0004_remove_house_concelho_remove_house_freguesia'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='listing_type',
            field=models.CharField(
                choices=[('rent', 'For Rent'), ('buy', 'For Sale')],
                default='rent',
                max_length=10
            ),
        ),
    ]
