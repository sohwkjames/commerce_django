# Generated by Django 3.0.8 on 2020-08-08 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_listing_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='watchlist',
            field=models.ManyToManyField(related_name='users', to='auctions.Listing'),
        ),
    ]
