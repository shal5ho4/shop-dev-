# Generated by Django 3.0.14 on 2021-10-13 10:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20211013_1024'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='dicount',
            new_name='discount',
        ),
    ]
