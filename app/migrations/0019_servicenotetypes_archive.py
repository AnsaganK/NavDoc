# Generated by Django 3.1.4 on 2021-08-31 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_auto_20210813_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicenotetypes',
            name='archive',
            field=models.BooleanField(default=False),
        ),
    ]