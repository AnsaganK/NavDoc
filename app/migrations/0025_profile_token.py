# Generated by Django 3.1.4 on 2021-06-15 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_auto_20210603_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='token',
            field=models.TextField(blank=True, null=True),
        ),
    ]