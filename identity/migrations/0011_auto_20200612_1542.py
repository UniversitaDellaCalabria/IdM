# Generated by Django 3.0.6 on 2020-06-12 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0010_auto_20200517_0116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='identity',
            name='gender',
            field=models.CharField(blank=True, choices=[('0', 'Not know'), ('1', 'Male'), ('2', 'Female'), ('9', 'Not specified')], max_length=3, null=True),
        ),
    ]
