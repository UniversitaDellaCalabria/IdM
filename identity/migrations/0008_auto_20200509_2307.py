# Generated by Django 3.0.5 on 2020-05-09 21:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0007_auto_20200509_2305'),
    ]

    operations = [
        migrations.RenameField(
            model_name='identity',
            old_name='telephone',
            new_name='telephoneNumber',
        ),
    ]
