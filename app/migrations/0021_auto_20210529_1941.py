# Generated by Django 3.1.7 on 2021-05-29 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_noteusers_date_create'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noteusers',
            name='date_create',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]