# Generated by Django 3.0.3 on 2020-02-29 10:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0002_auto_20200229_1716'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='room_date',
            new_name='book_date',
        ),
    ]
