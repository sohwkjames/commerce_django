# Generated by Django 3.0.8 on 2020-08-07 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20200805_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='image_url',
            field=models.CharField(blank=True, max_length=512),
        ),
    ]