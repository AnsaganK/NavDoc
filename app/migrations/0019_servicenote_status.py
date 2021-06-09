# Generated by Django 3.1.7 on 2021-05-27 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_servicenote_user_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicenote',
            name='status',
            field=models.CharField(blank=True, choices=[('success', 'Подписать'), ('edit', 'На редактирование'), ('error', 'Отказать')], max_length=200, null=True),
        ),
    ]