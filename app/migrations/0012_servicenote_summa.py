# Generated by Django 3.1.4 on 2021-05-26 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_noteusers'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicenote',
            name='summa',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
