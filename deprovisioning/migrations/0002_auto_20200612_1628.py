# Generated by Django 3.0.6 on 2020-06-12 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deprovisioning', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountupdatelog',
            name='type',
        ),
        migrations.AddField(
            model_name='accountupdatelog',
            name='event',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Event'),
        ),
        migrations.AlterField(
            model_name='accountupdatelog',
            name='uid',
            field=models.CharField(max_length=135, verbose_name='Account id'),
        ),
    ]