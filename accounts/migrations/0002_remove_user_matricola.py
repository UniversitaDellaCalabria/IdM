# Generated by Django 2.2.10 on 2020-02-11 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='matricola',
        ),
    ]
