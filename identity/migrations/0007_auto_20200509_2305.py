# Generated by Django 3.0.5 on 2020-05-09 21:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0006_auto_20200509_2302'),
    ]

    operations = [
        migrations.RenameField(
            model_name='identity',
            old_name='nation_of_bird',
            new_name='nation_of_birth',
        ),
    ]