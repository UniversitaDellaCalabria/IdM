# Generated by Django 2.2.10 on 2020-02-19 12:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_user_change_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='change_username',
        ),
    ]
