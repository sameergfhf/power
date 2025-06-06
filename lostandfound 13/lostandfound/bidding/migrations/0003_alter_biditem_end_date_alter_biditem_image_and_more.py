# Generated by Django 5.2 on 2025-04-16 17:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bidding', '0002_remove_biditem_admin_notes_alter_biditem_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biditem',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 4, 23, 17, 18, 59, 370, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='biditem',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='bid_items/'),
        ),
        migrations.AlterField(
            model_name='biditemimage',
            name='image',
            field=models.FileField(upload_to='bid_items/'),
        ),
    ]
