# Generated by Django 3.1.4 on 2021-05-24 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20210524_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='archive',
            field=models.BooleanField(default=False),
        ),
    ]
